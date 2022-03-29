import requests
from bs4 import BeautifulSoup
# import smtplib
# import email.mime.multipart
# import email.mime.text
import json
import schedule
import threading
import time
# TODO change print to logging
import logging


logging.basicConfig(filename='trace.log', filemode='w', level=logging.DEBUG)

def process():
    logging.debug("--- Starting to notify ---")
    print("--- Starting to notify ---")
    print("--- Opening configuration.json ---")

    f = open('./configuration.json')

    data = json.load(f)

    for i in data['config']:
        create_threaded_scheduler(i)

    f.close()

    # If we don't have a job we just exit the application
    if(len(schedule.get_jobs()) == 0):
        exit()

    while 1:
        schedule.run_pending()
        time.sleep(1)


def create_threaded_scheduler(config):
    # print("--- %s ---" %(config))

    if(not config['url'] or not config['condition'] or not config['cssSelector']):
        logging.error('--- No url, condition or cssSelector found in config: %s' %(config['name']))
        return

    lDefaultTime = 5
    if(hasattr(config, 'time')):
        lDefaultTime = config['time']

    # creating threaded scheduled task
    print("--- Created scheduled thread for %s in %d minutes---" %(config['name'], lDefaultTime))
    logging.debug("--- Created scheduled thread for %s in %d minutes---" %(config['name'], lDefaultTime))
    schedule.every(10).seconds.do(run_threaded, job, config)
        

def run_threaded(job_func, config):
    job_thread = threading.Thread(target=job_func(config))
    job_thread.start()

def job(config):
    
    page_text = requests.get(config['url']).text
    soup = BeautifulSoup(page_text, 'html.parser')
    print(config['cssSelector'])
    element = soup.select(config['cssSelector'])
    print(element)



if __name__ =="__main__":
    process()

