from google.cloud import pubsub_v1
import json
from google.auth import jwt

service_account_info = json.load(open("gcp_credential.json"))
publisher_audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"

credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=publisher_audience
)

credentials_pub = credentials.with_claims(audience=publisher_audience)

topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id="cryptic-opus-335323",
            topic='resources',
        )

publisher = pubsub_v1.PublisherClient(credentials=credentials_pub)
resources = ["https://api.mercadolibre.com/sites/MLA/search?category=MLA1459&PROPERTY_TYPE=242062&OPERATION=242075&state=TUxBUENBUGw3M2E1&neighborhood=TUxBQlZJTDI1ODla&price=1.5E7-*"]

for resource in resources:
    encoding = 'utf-8'
    encoded_resource = resource.encode(encoding)
    print("Publishing one message")
    future = publisher.publish(topic_name, encoded_resource)
    future.result()
