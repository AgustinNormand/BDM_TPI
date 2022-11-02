import requests
import time
import pickle
import sys
import csv
from google.cloud import storage
#from bs4 import BeautifulSoup
import lxml.html
import gzip
from requests_html import HTMLSession

session = HTMLSession()

def effectuate_request(permalink):
  r = session.get(permalink)
  if r.status_code == 200:
    if contains_specs_table(r.text):
      return [1, r.text]
  return [2, None]


def do_request(permalink):
  response_code, response_text = effectuate_request(permalink)
  if response_code == 1:
    upload(permalink, response_text)
  else:
    time.sleep(0.005)
    response_code, response_text = effectuate_request(permalink)
    if response_code == 1:
      upload(permalink, response_text)
    else:
      print('Try and Retry with error in {}'.format(permalink))

def contains_specs_table(request_text):
  try:
    parsed = lxml.html.fromstring(request_text)
    specs = parsed.find_class("ui-pdp-specs__table")[0]
    result = True
  except Exception as e:
    result = False
  return result
  
def upload_blob(blob, responses_file_name):
  uploaded = False
  try:
    blob.upload_from_filename(responses_file_name)
    uploaded = True
  except Exception as e:
    print("Upload try failed.")
    print("Exception [({})]".format(e))
  return uploaded
  
def upload(permalink, response):
  permalink_splited = str(permalink).split("/")
  name = permalink_splited[len(permalink_splited)-1]
  response_file_name = "{}.html".format(name)
  open_file = gzip.open(response_file_name, mode='wt')
  open_file.write(response)
  open_file.close()
 
  responses_blob_path = "html_scrapper/{}".format(response_file_name)

  blob = bucket.blob(responses_blob_path)
  
  uploaded_flag = False
  
  while not uploaded_flag:
    uploaded_flag = upload_blob(blob, response_file_name)
    if not uploaded_flag:
      print("Uploading blob failed, retrying")
      time.sleep(60)

workers = int(sys.argv[1]) #Cantidad de workers realizando peticiones
worker_number = int(sys.argv[2]) #Numero de worker que esta ejecutando este código

bucket_name = "bdm-unlu-rerun"
file_name = "dataset.csv"
blob_path = "attributes/{}".format(file_name)
#

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_path)
blob.download_to_filename(file_name)

print("Worker number arranca desde 0")

print("Workers: {}, Worker Number: {}".format(workers, worker_number))
  
permalinks = []
with open(file_name, newline='') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    permalinks.append(row['permalink'])

print("Permalinks len {}".format(len(permalinks)))

worker_size = len(permalinks) // workers

start_interval = 0 + ((worker_size)*worker_number)
finish_interval = start_interval + worker_size

print("Worker interval Start: {}, Finish {}".format(start_interval, finish_interval))

if (worker_number + 1) == workers:
  # Es el ultimo worker, agarro desde el start_interval hasta el final
  permalinks_worker = permalinks[start_interval:]
else:
  permalinks_worker = permalinks[start_interval:finish_interval]

print("Permalinks Worker Len {}".format(len(permalinks_worker)))

#open_file = gzip.GzipFile(responses_file_name, 'wb')

permalinks_with_errors = []

requests_done = 0

for permalink in permalinks_worker:
  try:
    do_request(permalink)
  except Exception as e:
    print("Error: Exception {}".format(e))
  time.sleep(0.005)

print("permalinks_with_errors: {}".format(permalinks_with_errors))
  





