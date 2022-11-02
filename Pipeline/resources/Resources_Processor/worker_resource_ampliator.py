from threading import Thread
import logging
import requests

class WorkerResourceAmpliator(Thread):
    def __init__(self, request_queue, headers, key):
        Thread.__init__(self)
        self.key = key
        self.queue = request_queue
        self.headers = headers
        self.ampliated_resources = []

    def get_values(self, available_filters, key):
        for filter in available_filters:
            if filter["id"] == key:
                return filter["values"]
        return None

    def run(self):
        while True:
            resource = self.queue.get()
            if resource == "":
                break
            try:
                limited_resource = "{}&limit=0&offset=0".format(resource)
                response = requests.get(limited_resource, headers=self.headers).json()
                available_filters = response["available_filters"]
                filter_values = self.get_values(available_filters, self.key)
                if filter_values != None:
                    for filter_value in filter_values:
                        self.ampliated_resources.append("{}&{}={}".format(resource, self.key, filter_value["id"]))
                else:
                    self.ampliated_resources.append(resource)
                    logging.info(
                        "filter_values in none, in ampliate_resources_with, response: {}, key: {}".format(
                            response, self.key))
            except Exception as e:
                logging.error("Exception: {}, Resource: {}".format(e, resource))
            self.queue.task_done()