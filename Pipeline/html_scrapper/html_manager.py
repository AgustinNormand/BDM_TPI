#import json
#from google.auth import jwt
from google.cloud import pubsub_v1
#import redis
#import time
import logging
#import sys
import json

from html_scrapper import Html_Scrapper


class Html_Manager():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('HtmlScrapperLogger')

        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.flow_control = pubsub_v1.types.FlowControl(max_messages=1)

        self.publish_topic = 'projects/{project_id}/topics/{topic}'.format(
                    project_id="cryptic-opus-335323",
                    topic='html_scrapper',
                )

        self.subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id="cryptic-opus-335323",
            sub='querys-sub',
        )

        self.hs = Html_Scrapper(self.logger)

        self.loop()

    def new_message_callback(self, message):
        self.logger.info("New message".format(message))
        try:
            encoding = 'utf-8'
            record = json.loads(message.data.decode(encoding))
            self.process_message(record)
            message.ack()
            self.logger.info("Ack message")
        except Exception as e:
            message.nack()
            self.logger.info("Nack message")
            self.logger.error(e)


    def process_message(self, record):
        processed_record = self.hs.request_and_process(record)
        if processed_record != None:
            encoding = 'utf-8'
            json_object = json.dumps(processed_record)
            future = self.publisher.publish(self.publish_topic, json_object.encode(encoding))
            future.result()

    def loop(self):
        future = self.subscriber.subscribe(self.subscription_name, self.new_message_callback, self.flow_control)
        future.result()


