# Flight-Delay-Analysis-in-HK-Airport
This project demonstrated an E2E process of analyzing delay time of all arrival flights in HK airport. Processes include 
1. Automatic Data Collection/Cleansing in Python
2. Data Storage in MongoDB
3. Predictive Modelling on delay time by XGBoost
4. REST API to support Predictive Modelling keep running in AWS EC2 Server
5. Data flow design and Dashboarding in JS by Node-Red

### Data Collection/Cleansing
Data from the government open source platform is used in this project. The open dataset is an open Restful API  which can be found on data.gov.hk1 published by the Hong Kong Airport Authority - https://data.gov.hk/en-data/dataset/aahk-team1-flight-info

Data collection and cleansing step will be triggered every 8AM HKT to collect the latest flight data of the day prior the running date.

![1](https://user-images.githubusercontent.com/29504448/71365869-3f66f900-25db-11ea-9bc4-fd4c390e5e41.png)

Following fields are kept after cleansing and being used in the analysis:
1. origin - Origin of the flight
2. baggage - Number of the baggage on the flight
3. hall - Arriving hall in HKG
4. terminal - Arriving terminal in HKG
5. stand - Parking stand number
6. flight - Airline and Flight number
7. statusCode - Latest status that airport update
8. data_dt - As of date of the data
9. stat_cde - Latest status that airport update
10. orig_dttm - Planned arrival time
11. status_dttm - Time of Latest status update
12. time_diff - Time difference of orig_dttm and status_dttm

All cleansed data are stored in MongoDB in this project

![2](https://user-images.githubusercontent.com/29504448/71365872-40982600-25db-11ea-8ab8-9d784c155ebd.png)

### Prediction and Dashboard Creation
Dashboard was mainly constructed by JS, with Node-Red, one form for user input and 4 charts were constructed in this dashboard. Node-Red will query data from MongoDB once received the input from user. And charts will be refreshed base on this request. Flow design as below.

![3](https://user-images.githubusercontent.com/29504448/71365874-41c95300-25db-11ea-8ac1-99147f22791d.png)

A classification model was build in python using XGBoost classifier, and hosted on Port 8012 with Restful API, so that when user input any flight number and date, Python API will response to the request and send the response to Nodered and show in the Dashboard.

![4](https://user-images.githubusercontent.com/29504448/71365879-43931680-25db-11ea-90f7-4b764685aa79.png)


### Outcome
![5](https://user-images.githubusercontent.com/29504448/71365882-455cda00-25db-11ea-9c55-cd8968c3eeea.png)

![6](https://user-images.githubusercontent.com/29504448/71365884-468e0700-25db-11ea-9398-c369db7495f9.png)







