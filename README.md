# Flight-Delay-Analysis-in-HK-Airport
This project demonstrated an E2E process of analyzing delay time of all arrival flight in HK airport. Process include 
1. Automatic Data collection/cleansing in Python
2. Data Storage in MongoDB
3. Predictive Modelling on delay time by XGBoost
4. REST API to support Predictive Modelling
5. Data flow design and Dashboarding by Node-Red

### Data Collection/Cleansing
Data from the government open source platform is used in this project. The open dataset is an open Restful API  which can be found on data.gov.hk1 published by the Hong Kong Airport Authority - https://data.gov.hk/en-data/dataset/aahk-team1-flight-info

Data collection and cleansing step will be triggerd every 8AM HKT to collect the latest flight data of the day prior the running date.

<--Screen Cap Data Collection flow-->

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

<--Screen Cap MongoDB-->

### Prediction and Dashboard Creation
Dashboard was mainly constructed by JS, with Node-Red, one form for user input and 4 charts were constructed in this dashboard. Node-Red will query data from MongoDB once received the input from user. And charts will be refreshed base on this request. Flow design as below.

<--Screen Cap Dashboard Flow-->

A classification model was build in python using XGBoost classifier, and hosted on Port 8012 with Restful API, so that when user input any flight number and date, Python API will response to the request and send the response to Nodered and show in the Dashboard.

<--Screen Cap Prediction Flow-->


### Outcome
<--Screen Cap Dashboard-->







