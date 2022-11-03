import json
import logging
import queue
import time

from google.auth import jwt
from google.cloud import pubsub_v1

from Resources_Processor.worker_paging_verificator import WorkerPagingVerificator
from Resources_Processor.worker_resource_ampliator import WorkerResourceAmpliator
from Meli_Autenticator.meli_autenticator import Meli_Autenticator


class Resources_Processor():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        ma = Meli_Autenticator(fresh_start=False)
        self.headers = {"Authorization": "Bearer {}".format(ma.get_access_token())}

    def start_brand_new(self):
        self.resources = []
        self.resources.append(
            'https://api.mercadolibre.com/sites/MLA/search?category=MLA1459&PROPERTY_TYPE=242062&OPERATION=242075&state=TUxBUENBUGw3M2E1')
        self.resources = self.ampliate_resources_with("neighborhood")

        start_time = time.time()
        logging.info("Resources ampliated len: {}, Execution time: {}".format(len(self.resources), time.time() - start_time))

        start_time = time.time()
        self.resources = self.ampliate_resources_with("price")
        logging.info("Resources re-ampliated len: {}, , Execution time: {}".format(len(self.resources), time.time() - start_time))

        start_time = time.time()
        logging.info("Trimmer Count: {}, Execution Time: {}".format(self.verify_paging(), time.time() - start_time))

        self.publish_resources()

    def ampliate_resources_with(self, key):
        q = queue.Queue()
        for resource in self.resources:
            q.put(resource)

        workers = []
        for _ in range(10):
            worker = WorkerResourceAmpliator(q, self.headers, key)
            worker.start()
            workers.append(worker)

        for _ in workers:
            q.put("")

        for worker in workers:
            worker.join()

        ampliated_resources = []
        for worker in workers:
            ampliated_resources.extend(worker.ampliated_resources)
        return ampliated_resources

    def verify_paging(self):
        q = queue.Queue()
        for resource in self.resources:
            q.put(resource)

        workers = []
        for _ in range(10):
            worker = WorkerPagingVerificator(q, self.headers)
            worker.start()
            workers.append(worker)

        for _ in workers:
            q.put("")

        for worker in workers:
            worker.join()

        trimmer_count = 0
        for worker in workers:
            trimmer_count += worker.trimmer_count
        return trimmer_count

    def publish_resources(self):
        service_account_info = json.load(open("./Resources_Processor/gcp_credential.json"))
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
        for resource in self.resources:
            encoding = 'utf-8'
            encoded_resource = resource.encode(encoding)
            future = publisher.publish(topic_name, encoded_resource)
            future.result()