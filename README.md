# py_web_scrape_notifier

A python script that notifies a user via email (only gmail) about specific changes to a website. (This requires a the gmail API). Have a closer look here: https://developers.google.com/gmail/api/quickstart/python. I use it with my rasbperry pi to get notified about prices changes for specific products.

The script uses

* schedule -> for time specfic scheduling (also each schedule in own thread)

* selenium or playwright -> for accessing the web page in headless browser mode with Chrome

* envelopes -> for sending the email (tried it also with the given smtp libs, but my email provider didn't like the format of the email)

## Limitations

Works only with a gmail account and with the gmail API. 

The application also uses env variables for the email and also the sender email and the receiver email. If you don't want to use that you can also just write the values hardcoded to the py file. The variables are the following

* sender_email -> the name of the email you want to sent from

* receiver_email -> the name of the email you want to sent to

## Setup

1. Just clone this repository. 

2. Setup virtual env for your cloned project. (I use windows, for unix you need to use python3). PS: It's better not to specify .env for this because of the .env file with the variables
   
   ```bash
   py -m venv something
   ```

3. Install dependencies
   
   ```bash
   py -m pip install -r requirements.txt
   ```

4. Change the configuration file to your desired needs

5. Adjust the .env file to your needs
   
   ```properties
   receiver_email = <some_email@some.com>
   sender_email = <some_email@gmail.com>
   ```

6. Set up your gmail API project. https://developers.google.com/gmail/api/quickstart/python

7. Start the application with 

```bash
py py_web_srape_notifier.py or py_web_srape_notifier_play.py
```

## Usage

To script uses the `configuration.json` to provide information about the to notify websites.

```json
{
  "config": [
    {
      "name": "test1",
      "url": "https://www.amazon.de/Apple-MacBook-Pro-Chip-10%E2%80%91Core-CPU-16%E2%80%91Core-GPU/dp/B09JR5JTP3/?_encoding=UTF8&pd_rd_w=78Cqh&pf_rd_p=07a6ea8f-9559-4d3e-86b6-bade19b6ee8e&pf_rd_r=HXVYGW3RVYEDR4AG9FHP&pd_rd_r=1ff8df8c-2834-4239-826d-e158795c3ba0&pd_rd_wg=hfjFi&ref_=pd_gw_ci_mcx_mr_hp_atf_m",
      "time": 1,
      "cssSelector": ".a-price-whole",
      "condition": "== True"
    },
    {
      "name": "test2",
      "url": "https://www.amazon.de/Apple-MacBook-Pro-Chip-10%E2%80%91Core-CPU-16%E2%80%91Core-GPU/dp/B09JR5JTP3/?_encoding=UTF8&pd_rd_w=78Cqh&pf_rd_p=07a6ea8f-9559-4d3e-86b6-bade19b6ee8e&pf_rd_r=HXVYGW3RVYEDR4AG9FHP&pd_rd_r=1ff8df8c-2834-4239-826d-e158795c3ba0&pd_rd_wg=hfjFi&ref_=pd_gw_ci_mcx_mr_hp_atf_m",
      "time": 1,
      "cssSelector": ".a-price-whole",
      "condition": "<= 2500"
    }
  ]
}
```

In the above configuration you can see two blocks, that are separate notifications. The first one checks if the `.a-price-whole` class exists on the given URL.

The second one checks, if the text of the `.a-price-whole` is less than 2500.

| Field       | Description                                                                                                                                              |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name        | The name of the notification. For the identification                                                                                                     |
| url         | The url of the website you want to get notified                                                                                                          |
| time        | The time the website is checked again (in min)                                                                                                           |
| cssSelector | The css selector. Here you can speficy everything that is possible with the css selector. Just check document.querySelector in your browser and try out. |
| condition   | When should the notification be send? Here you can specify your condition, when you should be informed about the change of the website                   |
