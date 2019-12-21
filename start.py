from flask import jsonify, Flask, request
import pickle
import json
from datetime import datetime
from util.clean_full_json import data_clean
from util.call_airport_api import request_flight_info, get_df_from_json

# Read xgb model
xgb_model_loaded = pickle.load(open("lib/xgb_reg.pkl", "rb"))

app = Flask(__name__)


@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    return jsonify(status=0)


# Depreciated
@app.route('/cleanData', methods=['GET', 'POST'])
def clean_data():
    if request.method == "POST":
        json_data = json.loads(request.json)
        # latest_dt = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0)
        cleaned_data = data_clean(json_data)
        return jsonify(json.dumps(cleaned_data.to_json()))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        request_json_data = request.json
        # print(request_json_data)
        # request_json_data = json.loads(request.json)
        try:
            json_data = request_flight_info(request_json_data['date'], request_json_data['flight_num'])
        except:
            return json.dumps(dict(response="Please input a valid date."))
        if json_data is not None:
            try:
                json_df = get_df_from_json(request_json_data['date'], json_data)
            except ValueError:
                return json.dumps(dict(response="Please input a valid date."))
            prob = xgb_model_loaded.predict_proba(json_df)[0, 1]
            print(prob)
            return json.dumps(dict(response="Probability being late > 30 mins for flight {} on {} is: {}".format(request_json_data['flight_num'], request_json_data['date'], round(prob, 3))))
        else:
            return json.dumps(dict(response="Flight does not exist on the day."))


app.run(host='0.0.0.0',
        port=8012,
        debug=True,
        use_reloader=False)

# Please run below code to test the API
# import requests
# import json
# # Case 1: There is such flight on that date
# post_data = {"date": "2019-11-17", "flight_num": "CX1724"}
# get_ = requests.post(url='http://localhost:8012/predict', json=json.dumps(post_data))
# print(get_.text)
# # Case 2: There is no such flight on that date
# post_data = {"date": "2019-11-17", "flight_num": "CX99999"}
# get_ = requests.post(url='http://localhost:8012/predict', json=json.dumps(post_data))
# print(get_.text)
