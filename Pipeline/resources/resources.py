from Pipeline.resources.Meli_Autenticator.meli_autenticator import Meli_Autenticator

import logging
import requests

import queue
import time
import urllib.request
from threading import Thread


class Worker(Thread):
    def __init__(self, request_queue):
        Thread.__init__(self)
        self.queue = request_queue
        self.errors = []
        self.counter = 0

    def run(self):
        while True:
            content = self.queue.get()
            if content == "":
                break
            try:
                #results = get_results(content)
                #self.counter += len(results)
                #append_to_file(results)
            except Exception as e:
                print(e)
                print("Resource: {}".format(content))
                self.errors.append(e)
            self.queue.task_done()

class Resources_Processor():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        ma = Meli_Autenticator(fresh_start=False)
        self.headers = {"Authorization": "Bearer {}".format(ma.get_access_token())}
        self.http_client = requests
        self.resources = []
        self.resources.append('https://api.mercadolibre.com/sites/MLA/search?category=MLA1459&PROPERTY_TYPE=242062&OPERATION=242075&state=TUxBUENBUGw3M2E1')

        self.resources = self.ampliate_resources_with("neighborhood")
        #print(len(self.resources))
        self.resources = self.ampliate_resources_with("price")
        #print(len(self.resources))

        self.verify_paging()

    def get_values(self, available_filters, key):
        for filter in available_filters:
            if filter["id"] == key:
                return filter["values"]
        return None

    def ampliate_resources_with(self, key):
        ampliated_resources = []
        for resource in self.resources:
            logging.info("Querying {}".format(resource))
            limited_resource = "{}&limit=0&offset=0".format(resource)
            response = self.http_client.get(limited_resource, headers=self.headers).json()
            available_filters = response["available_filters"]
            filter_values = self.get_values(available_filters, key)
            if filter_values != None:
                for filter_value in filter_values:
                    ampliated_resources.append("{}&{}={}".format(resource, key, filter_value["id"]))
            else:
                ampliated_resources.append(resource)
                logging.info("filter_values in none, in ampliate_resources_with, response: {}, key: {}".format(response, key))
        return ampliated_resources

    def verify_paging(self):
        for resource in self.resources:
            limited_resource = "{}&limit=0&offset=0".format(resource)
            paging = self.http_client.get(limited_resource, headers=self.headers).json()["paging"]
            logging.info("Querying {}".format(resource))
            if paging["total"] > 4000:
                logging.error("Paging > 4000 in {}".format(resource))