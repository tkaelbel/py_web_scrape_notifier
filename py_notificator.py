# import requests
# import bs4
# import smtplib
# import email.mime.multipart
# import email.mime.text
import json

def process():
    print("--- Starting to notify ---")
    print("--- Opening configuration.json ---")

    f = open('./configuration.json')

    data = json.load(f)

    for i in data['config']:
        create_scheduler(i)

    f.close()


def create_scheduler(config):

    print(config)

def 

if __name__ =="__main__":
    process()
