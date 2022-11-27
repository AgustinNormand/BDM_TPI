import base64
from google.cloud import pubsub_v1
from google.cloud import storage
import pandas as pd
import os
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt
from sklearn.model_selection import KFold


def download_files_if_needed():
    if not os.path.isfile("/tmp/train.csv"):
        storage_client = storage.Client()
        bucket = storage_client.bucket("bdm-unlu")
        blob = bucket.blob("21_train-test-split/train.csv")
        blob.download_to_filename("/tmp/train.csv")

    train = pd.read_csv("/tmp/train.csv")

    return train


def hello_pubsub(event, _):
    train = download_files_if_needed()

    decoded_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))

    print(decoded_message)
    features = decoded_message["features"]
    print("Features: {}".format(features))

    my_fold = decoded_message["fold"]
    n_splits = decoded_message["n_splits"]
    grid = decoded_message["grid"]
    tree = grid["tree"]
    grid.pop("tree")

    print("Tree: {}".format(tree))
    print("Grid: {}".format(grid))

    new_train = None  # Para que no tire un warning que tiraba
    validation = None  # Para que no tire un warning que tiraba
    kf = KFold(n_splits=n_splits)
    fold_number = 0
    for train_index, validation_index in kf.split(train):
        if fold_number == my_fold:
            new_train = train.iloc[train_index]
            validation = train.iloc[validation_index]
            break
        else:
            fold_number += 1

    x_train = new_train[features]
    y_train = new_train["price"]

    x_validation = validation[features]
    y_validation = validation["price"]

    if tree == 'RFRegressor':
        decoded_message["results"] = rf_regressor(grid, x_train, y_train, x_validation, y_validation)

    encoded_message = json.dumps(decoded_message).encode('utf-8')

    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id="cryptic-opus-335323",
        topic='rf_results',
    )
    future = pubsub_v1.PublisherClient().publish(topic_name, encoded_message)
    future.result()


def rf_regressor(grid, x_train, y_train, x_validation, y_validation):
    rf = RandomForestRegressor(n_jobs=-1, verbose=2)
    rf.set_params(**grid)
    rf.fit(x_train, y_train)

    y_pred = rf.predict(x_validation)

    results = {}
    mae = mean_absolute_error(y_validation, y_pred)
    results["mae"] = mae
    mse = mean_squared_error(y_validation, y_pred)
    results["mse"] = mse
    rmse = sqrt(mse)

    print('MAE: ', mae)
    print('MSE: ', mse)
    print("RMSE: ", rmse)

    results["rmse"] = rmse

    return results


def rf_regressor_neighborhood(grid, x_train, y_train, x_validation, y_validation):
    pass


def rf_regressor_neighborhood_rooms(grid, x_train, y_train, x_validation, y_validation):
    pass
