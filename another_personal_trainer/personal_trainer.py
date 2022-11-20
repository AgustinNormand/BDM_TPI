import functions_framework
from google.cloud import storage
import requests
import pandas as pd
import json
import os.path
import itertools as it
import requests
import queue
from threading import Thread

URL = "https://whey-protein-v6-anwfi3hvqq-uc.a.run.app"


def perform_web_requests(combinations, no_workers, data, parameters):
    class Worker(Thread):
        def __init__(self, request_queue, data, parameters):
            Thread.__init__(self)
            self.queue = request_queue
            self.data = data
            self.parameters = parameters

        def run(self):
            while True:
                content = self.queue.get()
                if content == "":
                    break
                message = {}
                message["features"] = list(self.data.columns)
                message["grid"] = {}
                for key, value in list(zip(self.parameters.keys(), list(content))):
                    message["grid"][key] = [value]
                encoded_resource = json.dumps(message)
                r = requests.post(URL, json=encoded_resource)
                print("Status Code {}".format(r.status_code))
                print("Response {}".format(r.content))
                self.queue.task_done()

    q = queue.Queue()
    for combination in combinations:
        q.put(combination)

    for _ in range(no_workers):
        q.put("")

    workers = []
    for _ in range(no_workers):
        worker = Worker(q, data, parameters)
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()

    return None


@functions_framework.http
def hello_http(request):

    if not os.path.isfile("/tmp/x_train.csv"):
        storage_client = storage.Client()
        bucket = storage_client.bucket("bdm-unlu")
        blob = bucket.blob("21_train-test-split/x_train.csv")
        blob.download_to_filename("/tmp/x_train.csv")

    data = pd.read_csv("/tmp/x_train.csv")

    parameters = {}
    pre_parameters = {}
    pre_parameters['n_estimators'] = [50, 3000, 50]

    for key in pre_parameters:
        final_list = []
        min, max, step = pre_parameters[key]
        for i in range(min, max, step):
            final_list.append(i)
        parameters[key] = final_list

    parameters["tree"] = ["RFRegressor"]

    all_keys = sorted(parameters)
    combinations = it.product(*(parameters[key] for key in all_keys))
    results = perform_web_requests(combinations, 10, data, parameters)
    return "Executed (:"