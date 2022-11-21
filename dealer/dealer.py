from google.cloud import pubsub_v1
from google.cloud import storage
import json
from datetime import datetime, timedelta
import threading
import pandas as pd
import time

last_message_timestamp = datetime.today()

output_data = {}

topic_name = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id="cryptic-opus-335323",
            sub='rf_results-sub',
        )

subscriber = pubsub_v1.SubscriberClient()

def old_execution_is_done():
    return datetime.today() > last_message_timestamp + timedelta(minutes=3)

class BackgroundTasks(threading.Thread):
    def save_and_upload_results(self):
        pd.DataFrame.from_dict(output_data).to_csv("whey_results.csv")
        storage_client = storage.Client()
        bucket = storage_client.bucket("bdm-unlu")
        blob = bucket.blob('whey_results.csv')
        blob.upload_from_filename('whey_results.csv')

    def run(self,*args,**kwargs):
        while True:
            if old_execution_is_done():
                print("Old execution is done")
                self.save_and_upload_results()
                break
            print("Execution is still going")                
            time.sleep(30)

t = BackgroundTasks().start()




def callback(message):
    print("New message")
    global best_precision
    global last_message_timestamp
    global best_combination
    global output_data
    last_message_timestamp = datetime.today()
    data = json.loads(message.data.decode("utf-8"))
    print(data)
    #results = data["results"]

    for key in data:
        #if type(data[key]) is dict:
        #    for subkey in data[key]:
        #        if not subkey in output_data:
        #            output_data[subkey] = [data[key][subkey]]
        #        else:
        #            output_data[subkey].append(data[key][subkey])
        #else:
        if key not in output_data:
            output_data[key] = [data[key]]
        else:
            output_data[key].append(data[key])

    message.ack()

future = subscriber.subscribe(topic_name, callback)
future.result()