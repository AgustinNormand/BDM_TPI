from google.cloud import pubsub_v1
from google.cloud import storage
import pandas as pd
import json
import os.path
import itertools as it

N_SPLITS = 5

if not os.path.isfile("x_train.csv"):
    storage_client = storage.Client()
    bucket = storage_client.bucket("bdm-unlu")
    blob = bucket.blob("21_train-test-split/x_train.csv")
    blob.download_to_filename("x_train.csv")

data = pd.read_csv("x_train.csv")

topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id="cryptic-opus-335323",
            topic='rf_parameters',
        )

publisher = pubsub_v1.PublisherClient()

parameters = {}

pre_parameters = {}
pre_parameters['n_estimators'] = [50, 1000, 50]
pre_parameters['min_samples_split'] = [2, 8, 2]
pre_parameters['min_samples_leaf'] = [1, 8, 2]

for key in pre_parameters:
    final_list = []
    min, max, step = pre_parameters[key]
    for i in range(min, max, step):
        final_list.append(i)
    parameters[key] = final_list

#parameters["tree"] = ["RFRegressor", "RFClassifier", "MultipleRFRegressor", "MRFRegressorRooms"]
parameters["tree"] = ["RFRegressor"]
parameters["criterion"] = ["squared_error", "absolute_error"]
parameters["max_features"] = ["sqrt"]



all_keys = sorted(parameters)
combinations = it.product(*(parameters[key] for key in all_keys))

#print("Parameters Keys {}".format(all_keys))
def send_combinations():
    for combination in list(combinations):
        #print("Combination: {}".format(combination))
        for split in range(N_SPLITS):
            message = {}
            message["features"] = list(data.columns)
            message["fold"] = split
            message["n_splits"] = N_SPLITS
            message["grid"] = {}
            for key, value in list(zip(all_keys, list(combination))):
                message["grid"][key] = value
            print("Message: {}".format(message))
            encoding = 'utf-8'
            encoded_resource = json.dumps(message)
            encoded_message = encoded_resource.encode(encoding)
            future = publisher.publish(topic_name, encoded_message)
            future.result()
        #break
    return "Executed (:"

send_combinations()