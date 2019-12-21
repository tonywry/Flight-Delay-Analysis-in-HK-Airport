#!/usr/bin/env python
# coding: utf-8

# In[1]:
import os
os.chdir("/home/ec2-user/COMP7503")

from datetime import datetime, timedelta
import json

latest_dt = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
print("Run Date "+latest_dt)


# In[2]:


flights = json.load(open("data/clean_json/clean_data_{}.json".format(latest_dt)))
for flight in flights:
    try:
        flight["data_dt"] = datetime.strptime(flight["data_dt"], "%Y-%m-%d")
        flight["orig_dttm"] = datetime.strptime(flight["orig_dttm"], "%Y-%m-%d %H:%M")
        flight["status_dttm"] = datetime.strptime(flight["status_dttm"], "%Y-%m-%d %H:%M")
    except:
        pass

print("Successfully load the data!")


# In[ ]:


import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["COMP7503"]
mycol = mydb["Flight Data"]
print("Successfully connect to DB!")

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




