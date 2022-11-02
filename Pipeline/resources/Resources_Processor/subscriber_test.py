import json
from google.auth import jwt
from google.cloud import pubsub_v1

service_account_info = json.load(open("./gcp_credential.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)

subscriber = pubsub_v1.SubscriberClient(credentials=credentials)

topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id="cryptic-opus-335323",
            topic='bdm',
        )

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id="cryptic-opus-335323",
    sub='bdm',
)

def callback(message):
    print(message.data)
    message.ack()

subscriber.create_subscription(name=subscription_name, topic=topic_name)
future = subscriber.subscribe(subscription_name, callback)
future.result()
