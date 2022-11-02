from Pipeline.resources.Resources_Processor.resources import Resources_Processor
import time
import logging

start_time = time.time()
Resources_Processor()
logging.info("Total Service Execution Time: {}".format(time.time() - start_time))