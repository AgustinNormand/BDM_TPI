import json
from google.auth import jwt
from google.cloud import pubsub_v1
import redis
import time
import logging

# DELETE
service_account_info = json.load(open("/home/agustin/GoogleApplicationCredentials.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)
# DELETE

from html_scrapper import Html_Scrapper


class Html_Manager():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('HtmlScrapperLogger')
        self.subscriber = pubsub_v1.SubscriberClient(credentials=credentials) # DELETE credentials

        self.topic_name = 'projects/{project_id}/topics/{topic}'.format(
                    project_id="cryptic-opus-335323",
                    topic='querys',
                )

        self.subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id="cryptic-opus-335323",
            sub='querys-sub',
        )

        #self.redis_client = redis.Redis(host='10.143.7.155', port=6379, db=0)

        self.hs = Html_Scrapper(self.logger)

        self.loop()

    def new_message_callback(self, message):
        self.logger.info("New message {}".format(message))
        encoding = 'utf-8'
        permalink = message.data.decode(encoding)
        try:
            self.process_message(permalink)
            message.ack()
            self.logger.info("Ack message")
        except Exception as e:
            message.nack()
            self.logger.info("Nack message")
            self.logger.error(e)

    def process_message(self, permalink):
        # UNCOMMENT
        #if self.redis_client.exists(permalink) == 0:
        #    self.logger.error("Permalink received not in redis, {}".format(permalink))
        #else:
        #    self.hs.request_and_process(permalink)
        self.hs.request_and_process(permalink)

    def loop(self):
        future = self.subscriber.subscribe(self.subscription_name, self.new_message_callback)
        future.result()


