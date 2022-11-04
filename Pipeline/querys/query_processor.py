import json
from google.auth import jwt
from google.cloud import pubsub_v1
import redis
import requests
import logging

from Meli_Autenticator.meli_autenticator import Meli_Autenticator
from records_processor import Records_Processor


class Query_Processor():
    def __init__(self):
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger('QueryLogger')

        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()

        self.publish_topic = 'projects/{project_id}/topics/{topic}'.format(
            project_id="cryptic-opus-335323",
            topic='querys',
        )

        self.subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id="cryptic-opus-335323",
            sub='resources-sub',
        )

        ma = Meli_Autenticator(fresh_start=False)

        self.headers = {"Authorization": "Bearer {}".format(ma.get_access_token())}

        self.rp = Records_Processor(self.logger)

        self.loop()

    def new_message_callback(self, message):
        self.logger.info("New message {}".format(message))
        encoding = 'utf-8'
        try:
            self.process_message(message.data.decode(encoding))
            message.ack()
            self.logger.info("Ack message")
        except Exception as e:
            self.logger.info("Nack message")
            self.logger.error(e)
            message.nack()


    def loop(self):
        future = self.subscriber.subscribe(self.subscription_name, self.new_message_callback)
        future.result()

    def get_request(self, resource, offset, limit):
        new_resource = resource+"&offset="+str(offset)+"&limit="+str(limit)
        return requests.get(new_resource, headers=self.headers).json()

    def get_results(self, resource):
        self.logger.info("Getting results of resource {}".format(resource))
        should_get = self.get_request(resource, 0, 0)["paging"]["total"]
        results = []
        records_remaining = True
        offset = 0
        last_len = 1
        while records_remaining:
            api_response = self.get_request(resource, offset, 50)["results"]
            results.extend(api_response)
            offset += 50
            if last_len == 0 and len(api_response) == 0:
                records_remaining = False
            last_len = len(api_response)
        self.logger.info("R: {}, Should Get: {}, Resource: {}".format(len(results), should_get, resource))
        return results

    def process_message(self, resource):
        encoding = 'utf-8'
        results = self.get_results(resource)
        processed_results = self.rp.process_results(results)
        for processed_result in processed_results:
            json_object = json.dumps(processed_result)
            future = self.publisher.publish(self.publish_topic, json_object.encode(encoding))
            future.result()