from threading import Thread
import logging
import requests

class WorkerPagingVerificator(Thread):
    def __init__(self, request_queue, headers):
        Thread.__init__(self)
        self.queue = request_queue
        self.headers = headers
        self.trimmer_count = 0

    def run(self):
        while True:
            resource = self.queue.get()
            if resource == "":
                break
            try:
                limited_resource = "{}&limit=0&offset=0".format(resource)
                response = requests.get(limited_resource, headers=self.headers).json()
                if response["paging"]["total"] > 4000:
                    self.trimmer_count += 1

            except Exception as e:
                logging.error("Exception: {}, Resource: {}".format(e, resource))
            self.queue.task_done()