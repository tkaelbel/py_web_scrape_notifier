# import requests
# import bs4
# import smtplib
# import email.mime.multipart
# import email.mime.text
import json
import schedule
import threading
import time

def process():
    print("--- Starting to notify ---")
    print("--- Opening configuration.json ---")

    f = open('./configuration.json')

    data = json.load(f)

    for i in data['config']:
        create_threaded_scheduler(i)

    f.close()

    while 1:
        schedule.run_pending()
        time.sleep(1)


def create_threaded_scheduler(config):
    print("--- Start to create scheduled thread for %s ---" %(config['name']))
    print("--- %s ---" %(config))

    lDefaultTime = 5
    if(hasattr(config, 'time')):
        lDefaultTime = config['time']

    # creating threaded scheduled task
    schedule.every(10).seconds.do(run_threaded, job, config)
    
    print(config)

def run_threaded(job_func, config):
    job_thread = threading.Thread(target=job_func(config))
    job_thread.start()

def job(config):
    print("This is a test")
    print(config['name'])

if __name__ =="__main__":
    process()

