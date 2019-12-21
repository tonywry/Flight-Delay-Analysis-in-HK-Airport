#!/usr/bin/env python
# coding: utf-8

# In[4]:


from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import ast
import json
import pandas as pd
import numpy as np

import os
os.chdir("/home/ec2-user/COMP7503")

date_list = []
for i in range(1,90):
    run_dt = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    if run_dt != "2019-09-07":
        date_list.append(run_dt)
date_list.reverse()


# #### Data Collection Part

# In[ ]:


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


# In[ ]:


for run_dt in date_list:
    print("scraping"+run_dt)   
    data_str = scrap_data("https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={}                            &%5Clang=en&cargo=false&arrival=true".format(run_dt))
    flights = ast.literal_eval(data_str)
    
    for flight in flights:
        flight["data_dt"] = run_dt
    print("Done Scraping successfully!")
    
    with open("data/raw_json/data_{}.json".format(run_dt), 'w') as f:
        json.dump(flights, f)
    print("output to raw_json successfully!")


# #### Data Cleansing Part

# In[ ]:




def clean_json(data_file):
    data = json.load(open(data_file))
    # Turn flight num from list to str
    # Turn origin from list to str
    for item in data:
        flight_no = ""
        orig = ""
        for flight in item["flight"]:
            flight_no = flight_no + "/"+flight["airline"]+"-"+flight["no"].replace(" ","")
            item["flight"] = flight_no[1:]
        for origin in item["origin"]:
            orig = orig + "/" +origin
            item["origin"] = orig[1:]
    return data

def clean_status(status):
    if "At gate" in status:
        stat_cde = "At gate"
        stat_time = status.replace("At gate ", "")
    elif "Est at" in status:
        stat_cde = "Est at"
        stat_time = status.replace("Est at ", "")
    elif "Landed" in status:
        stat_cde = "Landed"
        stat_time = status.replace("Landed", "")
    elif "Cancelled" in status:
        stat_cde = "Cancelled"
        stat_time = status.replace("Cancelled ", "")
    else:
        stat_cde = "None"
        stat_time = "None"
    return stat_cde, stat_time

# Clean status date, if the stat include the date info
def clean_status_time(x):
    if "(" in x:
        return x[:5]
    else:
        return x
    
def clean_status_date(x):
    if "(" in x:
        return x[7:-1]

def dttm2str(x):
    try:
        return x.strftime('%Y-%m-%d %H:%M')
    except:
        return ""
    
def data_clean(raw_json_file):    
    
    data_json_full = clean_json(raw_json_file)

    data_df = pd.DataFrame(data_json_full)
    data_df['stat_cde'], data_df['stat_time'] = zip(*data_df["status"].map(clean_status))
    data_df["status_tm"]=data_df["stat_time"].apply(clean_status_time)
    data_df["status_dt"]=data_df["stat_time"].apply(clean_status_date)
    data_df = data_df.drop(["status","stat_time"], axis=1).reset_index().iloc[:,1:]
    data_df = data_df.fillna("")

    # Clean status datetime / clean planed arrival time / calculate time diff in minutes
    for i in range(data_df.shape[0]):
        # if midnight, let the original arrival date = data_dt-1
        if data_df.loc[i,"status_dt"] != "":
            data_df.loc[i,"data_dt"] = datetime.strftime(datetime.strptime(data_df.loc[i,"data_dt"], "%Y-%m-%d")-timedelta(days=1), format="%Y-%m-%d")
        
        data_df.loc[i,"orig_dttm"] = datetime.strptime(data_df.loc[i,"data_dt"]+data_df.loc[i,"time"], "%Y-%m-%d%H:%M")
        
        if data_df.loc[i,"stat_cde"] not in ("Cancelled","None"):
            if data_df.loc[i,"status_dt"] != "":
                data_df.loc[i,"status_dttm"] = datetime.strptime(data_df.loc[i,"status_dt"]+data_df.loc[i,"status_tm"], "%d/%m/%Y%H:%M")
            else:
                data_df.loc[i,"status_dttm"] = datetime.strptime(data_df.loc[i,"data_dt"]+data_df.loc[i,"status_tm"], "%Y-%m-%d%H:%M")
            # Calculate time diff
            data_df.loc[i,"time_diff"] = (data_df.loc[i,"status_dttm"]-data_df.loc[i,"orig_dttm"]).total_seconds()/60.0
        else:
            data_df.loc[i,"status_tm"] = np.nan
            data_df.loc[i,"status_dt"] = np.nan
            data_df.loc[i,"time_diff"] = np.nan

    data_df = data_df.drop(["status_tm", "status_dt", "time"], axis=1)
    data_df['data_dt'] =  pd.to_datetime(data_df['data_dt'], format="%Y-%m-%d")
    
    # Change all date format to string before output JSON
    data_df['data_dt'] = data_df['data_dt'].apply(lambda x: x.strftime('%Y-%m-%d'))
    data_df['orig_dttm'] = data_df['orig_dttm'].apply(dttm2str)
    data_df['status_dttm'] = data_df['status_dttm'].apply(dttm2str)

    # Output the data_df as json
    data_df.to_json("data/clean_json/clean_data_{}.json".format(run_dt), orient='records')
    


# In[ ]:


for run_dt in date_list:
    print("Cleaning"+run_dt)
    data_clean("data/raw_json/data_{}.json".format(run_dt))


# #### Import MongoDB Part

# In[ ]:


import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["COMP7503"]
mycol = mydb["Flight Data"]
print("Successfully connect to DB!")


# In[ ]:


for run_dt in date_list:
    print("Importing"+run_dt)
    flights = json.load(open("data/clean_json/clean_data_{}.json".format(run_dt)))
    for flight in flights:
        try:
            flight["data_dt"] = datetime.strptime(flight["data_dt"], "%Y-%m-%d")
            flight["orig_dttm"] = datetime.strptime(flight["orig_dttm"], "%Y-%m-%d %H:%M")
            flight["status_dttm"] = datetime.strptime(flight["status_dttm"], "%Y-%m-%d %H:%M")
        except:
            pass

    for flight in flights:
        x = mycol.insert_one(flight)
    print("Successfully update DB!")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




