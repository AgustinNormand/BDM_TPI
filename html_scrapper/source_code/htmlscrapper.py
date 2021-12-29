import requests
import time
import pickle
import sys
import csv
from google.cloud import storage

workers = int(sys.argv[1]) #Cantidad de workers realizando peticiones
worker_number = int(sys.argv[2]) #Numero de worker que esta ejecutando este código

bucket_name = "bdm-unlu"
file_name = "dataset.csv"
blob_path = "attributes/{}".format(file_name)
responses_file_name = "responses_{}.pkl".format(worker_number)
responses_blob_path = "html_scrapper/{}".format(responses_file_name)

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_path)
blob.download_to_filename(file_name)

print("Worker number arranca desde 0")

print("Workers: {}, Worker Number: {}".format(workers, worker_number))
  
permalinks = []
with open('dataset.csv', newline='') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    permalinks.append(row['permalink'])

print("Permalinks len {}".format(len(permalinks)))

worker_size = len(permalinks) // workers

start_interval = 0 + ((worker_size)*worker_number)
finish_interval = start_interval + worker_size

print("Worker interval Start: {}, Finish {}".format(start_interval, finish_interval))

permalinks_worker = permalinks[start_interval:finish_interval]

print("Permalinks Worker Len {}".format(len(permalinks_worker)))

open_file = open(responses_file_name, "wb")

def append_to_file(permalink, response):
  pickle.dump([permalink, response], open_file)

def process_response(permalink, response):
  append_to_file(permalink, response.text)

permalinks_with_errors = []

requests_done = 0
error_count = 0

for permalink in permalinks_worker:
  try:
    r = requests.get(permalink)
    if r.status_code == 200:
      requests_done += 1
      process_response(permalink, r)
    else:
      print("Error")
      permalinks_with_errors.append(permalink)
      error_count += 1
  except Exception as e:
    permalinks_with_errors.append(permalink)
    print("Exception "+e)

  print("Requests Done: {}, Errors: {}".format(requests_done, error_count))
  time.sleep(0.1)

print("permalinks_with_errors: {}".format(permalinks_with_errors))
  
open_file.close()
  
blob = bucket.blob(responses_blob_path)

blob.upload_from_filename(responses_file_name)