import os, json, schedule, threading, time, logging
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from envelopes import Envelope

# Configure logging
logger = logging.getLogger(__name__)
fileLogger = logging.FileHandler(filename='trace.log', filemode='w', level=logging.INFO)
logger.addHandler(fileLogger)
logging.info("--- Hello from py_web_scrape_notifier ---")

# Selenium Chrome related variables
service = Service(executable_path=ChromeDriverManager().install())
op = webdriver.ChromeOptions()
op.add_argument('headless')


# Here we are getting the env variables from the os to set the email and password
# If you don't want to use env variables just put your email and password here as string
password = os.environ.get('EMAIL_PASSWORD')
sender_email = os.environ.get('SENDER_EMAIL')
receiver_email = os.environ.get('RECEIVER_EMAIL')
smtp_server = 'smtp.gmail.com'


# If password or sender_email or receiver_email are not defined, the program 
if(password is None or sender_email is None or receiver_email is None):
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

    driver.close()

# Creates a new Chrome based webdriver
def create_driver():
    return webdriver.Chrome(service=service, chrome_options=op)

# Evaluates the found element from the website with the configuration condition
def evaluate_condition(element, condition):
    value = None
    if('True' in condition or 'False' in condition):
        value = bool(element)
    else:
        ## TODO: here we need to find a different locale related solution
        value = float(element.text.replace('.', ''))
    
    condition_to_evaluate = f'{(value)} {condition}'
    return eval(condition_to_evaluate)

# Sends an email to the configured email
def send_notification(config):
    logger.info('--- Send notification for configuration %s ---', config['name'])

    msg = f'''\
    
    Your configuration {config['name']} has reached a true condition.
    Your CSS selector {config['cssSelector']}.
    The condition is the following {config['condition']}

    URL: {config['url']}

    '''
    envelope = Envelope(from_addr=sender_email, to_addr=receiver_email, 
        subject='Notification from py_web_scrape_notifier', text_body=msg)
    
    envelope.send(smtp_server, login=sender_email, password=password, tls=True)
    

if __name__ =="__main__":
    process()

