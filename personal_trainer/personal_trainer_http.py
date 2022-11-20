#from google.cloud import pubsub_v1
from google.cloud import storage
import requests
import pandas as pd
import json
import os.path
import itertools as it
#from flask import Flask
import requests

URL = "https://function-debug-anwfi3hvqq-uc.a.run.app"

#app = Flask(__name__)

if not os.path.isfile("x_train.csv"):
    storage_client = storage.Client()
    bucket = storage_client.bucket("bdm-unlu")
    blob = bucket.blob("21_train-test-split/x_train.csv")
    blob.download_to_filename("x_train.csv")

data = pd.read_csv("x_train.csv")

parameters = {}

pre_parameters = {}
pre_parameters['n_estimators'] = [50, 3000, 50]
#pre_parameters['min_samples_split'] = [2, 10, 2]
#pre_parameters['min_samples_leaf'] = [1, 7, 2]

for key in pre_parameters:
    final_list = []
    min, max, step = pre_parameters[key]
    for i in range(min, max, step):
        final_list.append(i)
    parameters[key] = final_list

#parameters["tree"] = ["RFRegressor", "RFClassifier", "MultipleRFRegressor", "MRFRegressorRooms"]
parameters["tree"] = ["RFRegressor"]

all_keys = sorted(parameters)
combinations = it.product(*(parameters[key] for key in all_keys))

def send_combinations():
    for combination in list(combinations):
        message = {}
        message["features"] = list(data.columns)
        message["grid"] = {}
        for key, value in list(zip(parameters.keys(), list(combination))):
            message["grid"][key] = [value]
        encoded_resource = json.dumps(message)
        r = requests.post(URL, json=encoded_resource)
        print("Status Code {}".format(r.status_code))
        print("Response {}".format(r.content))
        #encoded_message
        #future.result()
    return "Executed (:"