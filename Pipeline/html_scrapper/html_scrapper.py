from requests_html import HTMLSession
import time
#import requests
#import gzip
#from google.cloud import storage

from description_processor import Description_Processor
from image_count_processor import Image_Count_Processor
from spec_table_processor import Spec_Table_Processor


class Html_Scrapper():
    def __init__(self, logger):
        self.logger = logger
        self.error_count = 0
        self.session = HTMLSession()
        self.stp = Spec_Table_Processor()
        self.icp = Image_Count_Processor()
        self.dp = Description_Processor()

    def process_response(self, record, html):
        specs_table = self.stp.process_specs_table(html)
        self.logger.info("Specs Table: {}".format(specs_table))
        for key in specs_table:
            if key in record.keys():
                self.logger.error("Key of specs table shouldnt be in record")
            record[key] = specs_table[key]
        record["img_count"] = self.icp.process_image_count(html)
        self.logger.info("Img Count {}".format(record["img_count"]))
        record["description"] = self.dp.process_description(html)
        self.logger.info("Description {}".format(record["description"]))
        return record

    def request_and_process(self, record):
        time.sleep(0.005)
        #time.sleep(2)
        http_response = self.session.get(record["permalink"])
        contains_spec = self.stp.contains_specs_table(http_response.text)
        if http_response.status_code == 200 and contains_spec:
            return self.process_response(record, http_response.text)

        #time.sleep(3)
        new_http_response = self.session.get(record["permalink"])
        second_contains_spec = self.stp.contains_specs_table(new_http_response.text)
        if new_http_response.status_code == 200 and second_contains_spec:
            return self.process_response(record, new_http_response.text)
        else:
            self.error_count += 1
            self.logger.error("Actual Error Count {}, "
                              "Permalink {}, "
                              "First Status Code {}, "
                              "Second Status Code {}, "
                              "First Contains Spec {}, "
                              "Second Contains Spec {}.".format(
                self.error_count,
                record["permalink"],
                http_response.status_code,
                new_http_response.status_code,
                contains_spec,
                second_contains_spec))

            if new_http_response.status_code == 403 and http_response.status_code == 403:
                self.logger.error("403 and 403. Sleeping 2 minutes ? maybe works. Sleep time {}".format(time.time()))
                time.sleep(120)
                self.logger.error("Wake up time {}".format(time.time()))
            return None

