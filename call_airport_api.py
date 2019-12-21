import requests
import pandas as pd
from datetime import datetime
import json

# date = "2019-11-17"


def read_used_cols_dict():
    with open('lib/used_col_dict.txt') as json_file:
        used_col_dict = json.load(json_file)
    return used_col_dict


def request_flight_info(date, flight_num):
    link = "https://www.hongkongairport.com/" \
           "flightinfo-rest/rest/flights/past?date={date}&-lang=en&cargo=false&arrival=true"
    data = requests.get(link.format(date=date))
    data = data.text.replace('true', 'True').replace('false', 'False')
    data = eval(data)[-1]
    data = data['list']
    for row in data:
        for flight_ in row['flight']:
            if flight_['no'].replace(" ", "") == flight_num:
                return row
    return None

# test = request_flight_info("2019-11-17", "CX1724")


def get_df_from_json(date, json_):
    used_col_dict = read_used_cols_dict()
    df_dict = dict()
    # flights_collaborate
    df_dict['flights_collaborate'] = len(json_['flight'])
    # flight_stops
    df_dict['flight_stops'] = len(json_['origin'])
    # weekday
    for weekday in range(7):
        if weekday == datetime.strptime(date, '%Y-%m-%d').weekday():
            df_dict['weekday_{}'.format(weekday)] = 1
        else:
            df_dict['weekday_{}'.format(weekday)] = 0
    # origin period
    df_dict['orig_period_morning'] = 0
    df_dict['orig_period_afternoon'] = 0
    df_dict['orig_period_night'] = 0
    df_dict['orig_period_midnight'] = 0
    if (int(json_['time'][:2]) >= 0) & (int(json_['time'][:2]) <6):
        df_dict['orig_period_midnight'] = 1
    elif (int(json_['time'][:2]) >= 6) & (int(json_['time'][:2]) <12):
        df_dict['orig_period_morning'] = 1
    elif (int(json_['time'][:2]) >= 12) & (int(json_['time'][:2]) <18):
        df_dict['orig_period_afternoon'] = 1
    else:
        df_dict['orig_period_night'] = 1
    # airline
    for airline_ in [col.replace('airline_', '') for col in used_col_dict['cate_cols'] if 'airline_' in col]:
        df_dict['airline_{}'.format(airline_)] = max([1 if airline_ in i['no'][:2] else 0 for i in json_['flight']])
    # origin
    for origin_ in [col.replace('origin_', '') for col in used_col_dict['cate_cols'] if 'origin_' in col]:
        df_dict['origin_{}'.format(origin_)] = max([1 if origin_ in i else 0 for i in json_['origin']])
    df = pd.DataFrame.from_dict([df_dict])
    df = df[used_col_dict['col_order']]
    return df

# test_df = get_df_from_json('2019-11-17', test)

