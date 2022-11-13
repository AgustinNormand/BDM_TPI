import json
from google.auth import jwt
from google.cloud import pubsub_v1
import time
import sys

service_account_info = json.load(open("./gcp_credential.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)

subscriber = pubsub_v1.SubscriberClient(credentials=credentials)


subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id="cryptic-opus-335323",
    sub='html_scrapper-sub',
)

def callback(message):
    print(message.data)
    asd



future = subscriber.subscribe(subscription_name, callback)
future.result()
