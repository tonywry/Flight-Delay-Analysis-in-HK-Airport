#!/usr/bin/env python
# coding: utf-8

# #### Collect Data - https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date=2019-11-12&\lang=en&cargo=false&arrival=true

import os
os.chdir("/home/ec2-user/COMP7503")

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import ast
import json

latest_dt = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
print("Run Date "+latest_dt)



# Function to scrap data and clean to proper JSON format
def scrap_data(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    data_text = soup.text
    # if some data include info from diff days
    while True:
        try:
            data_text = data_text.replace(data_text[data_text.index("date")-2:data_text.index("date")+56],"")
        except:
            break
    return data_text.replace("]}","")



try:    
    data_str = scrap_data("https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={}                            &%5Clang=en&cargo=false&arrival=true".format(latest_dt))
    flights = ast.literal_eval(data_str)
    for flight in flights:
        flight["data_dt"] = latest_dt
    print("Done Scraping successfully!")
except:
    print("Error Occur!!")





with open('data/raw_json/data_{}.json'.format(latest_dt), 'w') as f:
    json.dump(flights, f)
print("data saved in COMP7503/data/raw_json")
