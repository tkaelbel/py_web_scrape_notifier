import locale
import json, schedule, threading, time, logging, os, pickle, platform
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode

from decouple import config

# Configure logging
logger = logging.getLogger(__name__)
fileLogger = logging.FileHandler(filename='trace.log', mode='w')
fileLogger.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
logger.addHandler(fileLogger)
logger.info("--- Hello from py_web_scrape_notifier ---")

op = Options()
op.headless = True

# Selenium Chrome related variables
if platform.system() == "Linux" and platform.machine() == "armv7l":
    print('rapsberry')  
    # if raspi
    op.BinaryLocation = ("/usr/bin/chromium-browser")
    service = Service("/usr/bin/chromedriver")
else:
    service = Service(executable_path=ChromeDriverManager().install())

# service = Service(executable_path=GeckoDriverManager().install())

# Here we are getting the env variables from the .env file to set the email
# If you don't want to use env variables just put your email here as string
sender_email = config('sender_email')
receiver_email = config('receiver_email')

SCOPES = ['https://mail.google.com/']

# Authenticate your email via gmail api. To set up have a look here https://developers.google.com/gmail/api/quickstart/python
def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as err:
                  logger.error("--- Could not read credentials.json because of %s---", err)
                  exit()
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

gmail_service = gmail_authenticate()

# If sender_email or receiver_email are not defined, the program 
if(sender_email is None or receiver_email is None or gmail_service is None):
    logger.info('--- Cannot send anything, because password or sender_email or receiver_email are None ---')
    logger.info('--- Please set the variables in this file or create the corresponding environment variables on your operating system ---')
    exit()


# Main entry method. This method checks whether the configuration file is available.
# If not the program will be exited.
# After that for each entry in the configuration file, the schedulers are created.
# To provied an endless processing, the wile loop at the end is used
def process():
    logger.info("--- Starting to notify ---")
    logger.info("--- Opening configuration.json ---")

    try:
        f = open('./configuration.json')
        data = json.load(f)
        f.close()
    except Exception as err:
        logger.error("--- Could not read configuration.json because of %s---", err)
        logger.info("--- Exiting app because no configuration ---")
        f.close()
        exit()

    for i in data['config']:
        create_threaded_scheduler(i)

    # If we don't have a job we just exit the application
    if(len(schedule.get_jobs()) == 0):
        logger.info("--- There are no scheduler jobs defined. Exiting app.. ---")
        exit()

    while 1:
        schedule.run_pending()
        time.sleep(1)

# Creates a new threaded schedule job for a given configuration
def create_threaded_scheduler(config):
    if(not config['url'] or not config['condition'] or not config['cssSelector']):
        logger.error('--- No url, condition or cssSelector found in config: %s ---', config['name'])
        return

    lDefaultTime = 5
    if(hasattr(config, 'time')):
        lDefaultTime = config['time']

    # creating threaded scheduled task
    logger.info("--- Created scheduled thread for %s in %d minutes ---", config['name'], lDefaultTime)
    schedule.every(lDefaultTime).seconds.do(run_threaded, job, config)
        
# Runs the threaded scheduled job
def run_threaded(job_func, config):
    job_thread = threading.Thread(target=job_func(config))
    job_thread.start()

# Executes a threaded scheduled job
# Creates a new webdriver instances to navigate headless to the given URL from the config
# Tries to get the element from the website
# Tries to evaluate the given condition
# Calls, the send_notification, if the condition is true
def job(config):
    logger.info('--- Processing for configuration %s ---', config['name'])
        
    try:
        driver = create_driver()
        driver.get(config['url'])
        time.sleep(5)
        logger.info('--- Accessing given URL by Selenium ---')

        element = driver.find_element(By.CSS_SELECTOR, value=config['cssSelector'])
        logger.info('--- Found given css selector element ---')

        logger.info('--- Trying to evaluate condition %s ---', config['condition'])
        condition = config['condition']
        evaluated_condition = evaluate_condition(element, condition)
        logger.info('--- Successfully evaluated condition ---')

        if(evaluated_condition):
            send_notification(config)

    except NoSuchElementException as err:
        logger.error('--- Could not find element because of %s ---', err)
    except Exception as err1:
        logger.error('--- Could not evaluate conidition because of %s ---', err1)

    if(driver is not None):
        driver.close()

def create_driver():
    return webdriver.Chrome(service=service, options=op)

# Evaluates the found element from the website with the configuration condition
def evaluate_condition(element, condition):
    value = None
    if('True' in condition or 'False' in condition):
        value = bool(element)
    else:
        value = locale.atof(element.text)
    
    condition_to_evaluate = f'{(value)} {condition}'
    return eval(condition_to_evaluate)

# Sends an email to the configured email
def send_notification(config):
    logger.info('--- Send notification for configuration %s ---', config['name'])

    gmail_service.users().messages().send(
        userId='me',
        body=build_message(config)
    ).execute()


def build_message(config):
    msg = f'''\
    
    Your configuration {config['name']} has reached a true condition.
    Your CSS selector {config['cssSelector']}.
    The condition is the following {config['condition']}

    URL: {config['url']}

    '''

    message = MIMEText(msg)
    message['to'] = receiver_email
    message['from'] = sender_email
    message['subject'] = 'Notification from py_web_scrape_notifier'

    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

if __name__ =="__main__":
    process()

