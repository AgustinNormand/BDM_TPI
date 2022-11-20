import functions_framework
import base64
from google.cloud import pubsub_v1
from google.cloud import storage
import pandas as pd
import os
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error,  mean_absolute_error
from math import sqrt

def download_files_if_needed():
    if not os.path.isfile("x_train.csv") or not os.path.isfile("y_train.csv") or not os.path.isfile("x_test.csv") or not os.path.isfile("y_test.csv"):
        storage_client = storage.Client()
        bucket = storage_client.bucket("bdm-unlu")
        blob = bucket.blob("21_train-test-split/x_train.csv")
        blob.download_to_filename("/tmp/x_train.csv")
        blob = bucket.blob("21_train-test-split/y_train.csv")
        blob.download_to_filename("/tmp/y_train.csv")
        blob = bucket.blob("21_train-test-split/x_test.csv")
        blob.download_to_filename("/tmp/x_test.csv")
        blob = bucket.blob("21_train-test-split/y_test.csv")
        blob.download_to_filename("/tmp/y_test.csv")

    x_train_original = pd.read_csv("/tmp/x_train.csv")
    x_test_original = pd.read_csv("/tmp/x_test.csv")
    y_train_original = pd.read_csv("/tmp/y_train.csv")
    y_test_original = pd.read_csv("/tmp/y_test.csv")

    return [x_train_original, x_test_original, y_train_original, y_test_original]

def rf_regressor(grid, x_test, x_train, y_train_original, y_test_original):
    rf = RandomForestRegressor(n_jobs=-1, verbose=2)
    rf_random = GridSearchCV(estimator = rf, param_grid = grid, cv = 5, verbose=2, n_jobs = -1)
    rf_random.fit(x_train, y_train_original)

    y_pred = rf_random.predict(x_test)

    results = {}
    mae = mean_absolute_error(y_test_original, y_pred)
    results["mae"] = mae
    mse = mean_squared_error(y_test_original, y_pred)
    results["mse"] = mse
    rmse = sqrt(mse)

    print('MAE: ', mae)
    print('MSE: ', mse)
    print("RMSE: ", rmse)

    results["rmse"] = rmse

    return results


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    x_train_original, x_test_original, y_train_original, y_test_original = download_files_if_needed()

    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(name)
