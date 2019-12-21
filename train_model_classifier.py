import pandas as pd
import xgboost
from sklearn.model_selection import train_test_split
from sklearn.tree import ExtraTreeClassifier
import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
import pickle
import json
from sklearn.model_selection import GridSearchCV

SEED = 1102

df = pd.read_csv('data/data_nosplit.csv')

# Filter
df = df[df['statusCode'] == 'ON']
df.drop(['terminal', 'stat_cde', 'statusCode'], axis=1, inplace=True)

# Clean and transform
for cols in ['data_dt', 'orig_dttm', 'status_dttm']:
    df[cols] = pd.to_datetime(df[cols])

df['weekday'] = df['data_dt'].dt.weekday.astype(str)
df.loc[(df['orig_dttm'].dt.hour >= 0)&(df['orig_dttm'].dt.hour < 6), 'orig_period'] = 'midnight'
df.loc[(df['orig_dttm'].dt.hour >= 6)&(df['orig_dttm'].dt.hour < 12), 'orig_period'] = 'morning'
df.loc[(df['orig_dttm'].dt.hour >= 12)&(df['orig_dttm'].dt.hour < 18), 'orig_period'] = 'afternoon'
df.loc[(df['orig_dttm'].dt.hour >= 18)&(df['orig_dttm'].dt.hour < 24), 'orig_period'] = 'night'

all_flight_list = "/".join(df.flight)
all_flight_list = all_flight_list.split("/")
all_airline_code = []
for flight_ in all_flight_list:
    all_airline_code.append(flight_.split('-')[1][:2])
all_airline_code = list(set(all_airline_code))
for airline in all_airline_code:
    df['airline_{}'.format(airline)] = np.where(df['flight'].str.contains("-{}".format(airline)), 1, 0)
df['flight_stops'] = df['origin'].str.count("/") + 1
df['flights_collaborate'] = df['flight'].str.count("/") + 1

all_origin_list = "/".join(df.origin)
all_origin_list = all_origin_list.split("/")
all_origin_list = list(set(all_origin_list))
for origin in all_origin_list:
    df['origin_{}'.format(origin)] = np.where(df['origin'].str.contains(origin), 1, 0)

cate_cols1 = ['weekday', 'orig_period']
num_cols = ['flight_stops', 'flights_collaborate']
x_cate = pd.concat([pd.get_dummies(df[cate_cols1]), df[[cols for cols in df.columns if ("airline_" in cols) |
                                                        ('origin_' in cols)]]], axis=1)
x_num = df[num_cols]
x_ = pd.concat([x_cate, x_num], axis=1)
y_ = (df['time_diff'] > 30) * 1

# Train test split
x_train, x_test, y_train, y_test = train_test_split(x_, y_, stratify=y_, test_size=0.3, random_state=SEED)
tree_ = ExtraTreeClassifier(random_state=SEED)
tree_.fit(x_train, y_train)
imp_ = pd.DataFrame(tree_.feature_importances_.reshape(1, -1),
                    columns=np.array(x_train.columns).flatten(),
                    index=['imp']).T
imp_ = imp_.sort_values('imp', ascending=False).reset_index()
# imp_.loc[0:60, 'imp'].sum() # sum of var imp = 0.806
imp_feat = imp_.loc[0:60, 'index'].to_list()

model = xgboost.XGBClassifier(learning_rate=0.02,
                              max_depth=3,
                              n_estimators=600,
                              min_child_weight=0,
                              reg_lambda=1,
                              seed=SEED,
                              n_jobs=10,
                              scale_pos_weight=6)
model.fit(x_train[imp_feat], y_train)
train_pred_prob = model.predict_proba(x_train[imp_feat])
test_pred_prob = model.predict_proba(x_test[imp_feat])

print(roc_auc_score(y_train, train_pred_prob[:, 1]))
print(roc_auc_score(y_test, test_pred_prob[:, 1]))

print(confusion_matrix(y_train, (train_pred_prob[:, 1]>0.5)*1))
print(confusion_matrix(y_test, (test_pred_prob[:, 1]>0.5)*1))


# Save model and columns
file_name = "lib/xgb_reg.pkl"
pickle.dump(model, open(file_name, "wb"))

used_col_dict = dict()
used_col_dict['num_cols'] = [cols for cols in imp_feat if cols in ['flight_stops', 'flights_collaborate']]
used_col_dict['cate_cols'] = [cols for cols in imp_feat if cols not in used_col_dict['num_cols']]
used_col_dict['col_order'] = list(x_train[imp_feat].columns)
with open('lib/used_col_dict.txt', 'w') as outfile:
    json.dump(used_col_dict, outfile)

# load model
# file_name = "lib/xgb_reg.pkl"
# xgb_model_loaded = pickle.load(open(file_name, "rb"))

# load cols
# with open('lib/used_col_dict.txt') as json_file:
#     used_col_dict = json.load(json_file)



# grid search
# parameters = {
#               'max_depth': [3, 5, 7, 10],
#               'learning_rate': [0.01, 0.02, 0.05, 0.1, 0.3],
#               'n_estimators': [100, 500, 1000, 2000],
#               'min_child_weight': [0, 2, 5, 10, 20],
#               'max_delta_step': [0, 0.2, 0.6, 1],
#               'subsample': [0.6, 0.8, 0.9, 1],
#               'colsample_bytree': [0.8, 0.9],
#               'reg_alpha': [0, 0.25, 1],
#               'reg_lambda': [0.2, 0.6, 1],
#               'scale_pos_weight': [1, 3, 7, 10],
# }
# xlf = xgboost.XGBClassifier(max_depth=10,
#                             learning_rate=0.01,
#                             n_estimators=2000,
#                             silent=True,
#                             objective='binary:logistic',
#                             nthread=-1,
#                             gamma=0,
#                             min_child_weight=1,
#                             max_delta_step=0,
#                             subsample=0.85,
#                             colsample_bytree=0.7,
#                             colsample_bylevel=1,
#                             reg_alpha=0,
#                             reg_lambda=1,
#                             scale_pos_weight=1,
#                             seed=1440,
#                             missing=None)
#
#
# gsearch = GridSearchCV(xlf, param_grid=parameters, scoring='f1', cv=5)
# gsearch.fit(x_train[imp_feat], y_train)
#
# print("Best score: %0.3f" % gsearch.best_score_)
# print("Best parameters set:")
# best_parameters = gsearch.best_estimator_.get_params()
# for param_name in sorted(parameters.keys()):
#     print("\t%s: %r" % (param_name, best_parameters[param_name]))
