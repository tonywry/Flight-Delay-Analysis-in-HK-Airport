# Flight-Delay-Analysis-in-HK-Airport
This project demonstrated an E2E process of analyzing delay time of all arrival flight in HK airport. Process include 
1. Automatic Data collection/cleansing in Python
2. Data Storage in MongoDB
3. Predictive Modelling on delay time by XGBoost
4. REST API to support Predictive Modelling
5. Data flow design and Dashboarding by Node-Red

### Data Collection/Cleansing
Data from the government open source platform is used in this project. The open dataset is an open Restful API  which can be found on data.gov.hk1 published by the Hong Kong Airport Authority - https://data.gov.hk/en-data/dataset/aahk-team1-flight-info

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

### Prediction and Dashboard Creation



### Outcome



