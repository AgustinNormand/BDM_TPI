import requests
import time
import pickle
import sys
import csv
from google.cloud import storage
import gzip
import queue
from threading import Thread


api_key = "AIzaSyAXGKVsLpRsDJitNvZCFfowsV0oZ8sRO88"

def build_places_url(lat, long, a_type):
  return f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius=500&type={a_type}&key={api_key}"
  #return f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius=500&types={types}"


def build_places_url(lat, long):
  return f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius=500&key={api_key}"
  #return f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius=500&types={types}"


def build_extra_results_places_url(token):
  return f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={token}&key={api_key}"
  #return f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={token}"


def build_establishments(response):
#  if ("next_page_token" in response):    
#    request_count = 0
#    next_page_url = build_extra_results_places_url(response["next_page_token"])    
#    time.sleep(1)                                 
#    next_page = requests.get(next_page_url).json()
#    while(next_page["status"] == "INVALID_REQUEST" and request_count < 10):
#      time.sleep(1)
#      next_url = next_page_url + "&request_count=" + str(request_count) # We add the request count to the query in order to avoid caching
#      next_page = requests.get(next_url).json() 
#      request_count += 1
#    return response["results"] + build_establishments(next_page)  
#  else: 
  return response["results"]

def perform_web_requests(addresses, no_workers):
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
                #for url in content[1]:
                url = content[1]
                try:
                  response = requests.get(url).json()
                  establishments = build_establishments(response)                  
                  self.counter += 1
                  if (self.counter % 100 == 0):
                    print(f"100 permalinks consultados. Counter: {self.counter}")
                  append_to_file(content[0], establishments)
                except Exception as e:
                  print(f"Error generando consulta {e} para url {url}")
                  self.errors.append([e, content[0], url])
                self.queue.task_done()

    q = queue.Queue()
    for url in addresses:
        q.put(url)

    workers = []
    for _ in range(no_workers):
        worker = Worker(q)
        worker.start()
        workers.append(worker)

    for _ in workers:
        q.put("")

    for worker in workers:
        worker.join()

    e = []
    record_count = 0
    for worker in workers:
        e.extend(worker.errors)
        record_count += worker.counter

    return [e, record_count]


## Funciones para guardar el trabajo de los workers
def append_to_file(permalink, response):
  pickle.dump([permalink, response], open_file)


workers = int(sys.argv[1]) #Cantidad de workers realizando peticiones
worker_number = int(sys.argv[2]) #Numero de worker que esta ejecutando este código

bucket_name = "bdm-unlu"
file_name = "trimmed_dataset_cf.csv"
blob_path = "dataset_trimmer/{}".format(file_name)
responses_file_name = "responses_{}.pkl".format(worker_number)
responses_blob_path = "google_places/{}".format(responses_file_name)

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_path)
blob.download_to_filename(file_name)

print("Worker number arranca desde 0")

print("Workers: {}, Worker Number: {}".format(workers, worker_number))
  
data = []

included_types = "hospital", "restaurant", "park", "subway_station", "bus_station", "school", "supermarket", "laundry", "parking", "gym"

with open(file_name, newline='') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    #urls = []
    #for a_type in included_types:
    # urls.append(build_places_url(row['latitude'], row['longitude'], a_type))     
    data.append([row['permalink'], build_places_url(row['latitude'], row['longitude'])])

print("Data len {}".format(len(data)))

worker_size = len(data) // workers

start_interval = 0 + ((worker_size)*worker_number)
finish_interval = start_interval + worker_size

print("Worker interval Start: {}, Finish {}".format(start_interval, finish_interval))

if (worker_number + 1) == workers:
  # Es el ultimo worker, agarro desde el start_interval hasta el final
  worker_data = data[start_interval:]
else:
  worker_data = data[start_interval:finish_interval]

print("Data Worker Len {}".format(len(worker_data)))

open_file = gzip.GzipFile(responses_file_name, 'wb')

entry_with_errors = []

requests_done = 0
error_count = 0

errors, record_count = perform_web_requests(worker_data, 25)

print("data_with_errors: {}".format(entry_with_errors))
  
open_file.close()
  
blob = bucket.blob(responses_blob_path)

def upload_blob(blob, responses_file_name):
  uploaded = False
  try:
    blob.upload_from_filename(responses_file_name)
    uploaded = True
  except Exception as e:
    print("Upload try failed.")
    print("Exception [({})]".format(e))
  return uploaded

uploaded_flag = False
while not uploaded_flag:
  print("Trying to upload blob")
  uploaded_flag = upload_blob(blob, responses_file_name)
  if not uploaded_flag:
    time.sleep(60)


