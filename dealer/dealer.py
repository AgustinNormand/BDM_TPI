from google.cloud import pubsub_v1
import json
from datetime import datetime, timedelta

best_precision = -1
best_combination = {}
last_message_timestamp = datetime.today()

topic_name = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id="cryptic-opus-335323",
            sub='rf_results-sub',
        )

subscriber = pubsub_v1.SubscriberClient()

def old_execution_is_done():
    return datetime.today() > last_message_timestamp + timedelta(minutes=3)

def reset_execution():
    global best_combination
    global best_precision
    print("Best parameters so far: {}".format(best_combination))
    print("Starting new execution")
    best_precision = -1
    best_combination = {}

def callback(message):
    global best_precision
    global last_message_timestamp
    global best_combination
    if old_execution_is_done():
        reset_execution()
    last_message_timestamp = datetime.today()
    data = json.loads(message.data.decode("utf-8"))
    print(data)
    results = data["results"]
    mae = results["mae"]
    if mae > best_precision:
        best_precision = mae
        best_combination = data
    message.ack()

future = subscriber.subscribe(topic_name, callback)
future.result()