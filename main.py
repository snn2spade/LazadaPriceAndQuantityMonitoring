import json
import re
import time

import requests
from bs4 import BeautifulSoup

# SETUP HERE
chanel_access_token = "3Xwxc9Ytd2rvlPzcbgEIbxSzXVA/nKu3e3rjg57ODMuaYBrAw9i0AUxAScowQvw6VY06KRL5fkGdYHa9KwG3VovvUWj+kwoFmcd7SWOSsBD4Rf1YEvS++NHLzXP/Sj/QMVHj+wGyuQPWwQVjKM9htgdB04t89/1O/w1cDnyilFU="
monitor_url = "https://www.lazada.co.th/products/apple-iphone-xr-i259756890-s399955728.html/"
server_status_refresh_every = 3600  # Sec
refresh_interval = 5  # Sec

##################

def extract_price_and_max_quantity(event, context):
    response = requests.get(monitor_url)
    soup = BeautifulSoup(response.text, "html.parser")
    max_quantity = int(soup.find("span", {"class": "next-input-single"}).input["max"])
    price = soup.find("span", {"class": "pdp-price"}).text
    try:
        price = re.search('\d+(,\d{3})*(\.\d+)?', price).group(0)
    except AttributeError as err:
        print("Cannot convert extract money-like-string from price text")
    return {"price": price, "max_quantity": max_quantity}


def get_payload(text):
    return {
        "to": "Ufdfb4259661ae9c8e396d50087547d86",
        "messages": [{"type": "text", "text": text}]
    }


def get_headers():
    return {"Content-Type": "application/json", "Authorization":
        "Bearer {}".format(chanel_access_token)}


def send_line_msg(text):
    r = requests.post("https://api.line.me/v2/bot/message/push", data=json.dumps(get_payload(text))
                      , headers=get_headers())


total_sleep = 0
send_line_msg("Start monitoring..")
# Do
response = extract_price_and_max_quantity(None, None)
prev_max_quantity = response["max_quantity"]
prev_price = response["price"]
send_line_msg("Server Started with Price = {}, Max Quantity = {}".format(prev_price, prev_max_quantity))
while (True):
    print("Running...")
    time.sleep(refresh_interval)
    total_sleep += refresh_interval
    response = extract_price_and_max_quantity(None, None)
    max_quantity = response["max_quantity"]
    price = response["price"]

    if max_quantity != prev_max_quantity:
        send_line_msg("Max quantity has changed to {}".format(max_quantity))
        prev_max_quantity = max_quantity

    if price != prev_price:
        send_line_msg("Price has changed to {}".format(price))
        prev_price = price
    if total_sleep >= server_status_refresh_every:
        total_sleep = 0
        send_line_msg("Server Status still up. Price = {}, Max Quantity = {}".format(price, max_quantity))
