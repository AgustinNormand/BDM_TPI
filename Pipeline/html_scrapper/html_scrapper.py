from requests_html import HTMLSession
import gzip
from google.cloud import storage

from description_processor import Description_Processor
from image_count_processor import Image_Count_Processor
from spec_table_processor import Spec_Table_Processor


class Html_Scrapper():
    def __init__(self, logger):
        self.logger = logger
        self.session = HTMLSession()
        self.stp = Spec_Table_Processor()
        self.icp = Image_Count_Processor()
        self.dp = Description_Processor()


    def request_and_process(self, permalink):
        http_response = self.session.get(permalink)
        if http_response.status_code == 200:
            if self.stp.contains_specs_table(http_response.text):
                specs_table = self.stp.process_specs_table(http_response.text)
                self.logger.info("Specs Table: {}".format(specs_table))
                image_count = self.icp.process_image_count(http_response.text)
                decription = self.dp.process_description(http_response)
