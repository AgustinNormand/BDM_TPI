import logging
from threading import Thread

import requests


class WorkerPagingVerificator(Thread):
    def __init__(self, request_queue, headers):
        Thread.__init__(self)
        self.queue = request_queue
        self.headers = headers
        self.trimmer_count = 0
        self.record_paging_count = 0

    def run(self):
        while True:
            resource = self.queue.get()
            if resource == "":
                break
            try:
                limited_resource = "{}&limit=0&offset=0".format(resource)
                response = requests.get(limited_resource, headers=self.headers).json()
                total_paging = response["paging"]["total"]
                if total_paging > 4000:
                    self.trimmer_count += 1
                self.record_paging_count += total_paging

            except Exception as e:
                logging.error("Exception: {}, Resource: {}".format(e, resource))
            self.queue.task_done()