import requests
import time
import pickle
import sys
import csv
from google.cloud import storage
import gzip
import queue
from threading import Thread


api_key = ""

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
  if ("next_page_token" in response):    
    request_count = 0
    next_page_url = build_extra_results_places_url(response["next_page_token"])    
    time.sleep(1)                                 
    next_page = requests.get(next_page_url).json()
    while(next_page["status"] == "INVALID_REQUEST" and request_count < 10):
      time.sleep(1)
      next_url = next_page_url + "&request_count=" + str(request_count) # We add the request count to the query in order to avoid caching
      next_page = requests.get(next_url).json() 
      request_count += 1
    return response["results"] + build_establishments(next_page)  
  else: 
    return response["results"]

def perform_web_requests(addresses, no_workers):

    class Printer(Thread):
      def __init__(self, out_queue):
            Thread.__init__(self)
            self.out_queue = out_queue

      def run(self):
            while True:
                content = self.out_queue.get()
                append_to_file(content)
                self.out_queue.task_done()

    class Worker(Thread):
        def __init__(self, request_queue, worker_number, out_queue):
            Thread.__init__(self)
            self.queue = request_queue
            self.errors = []
            self.counter = 0
            self.worker_number = worker_number
            self.out_queue = out_queue

        def run(self):
            while True:
                content = self.queue.get()

                try:
                  response = requests.get(content[1])
                  if response.status_code != 200:
                    print("Status code != 200")
                  establishments = build_establishments(response.json())  

                  if self.worker_number == 0:
                    print("Worker 0 doing request number {} Establishments len {}. Status Code {}.".format(content[2], len(establishments), response.status_code))

                  self.out_queue.put([content[0], establishments])
                  self.counter += 1
                except Exception as e:
                  print("Error generando consulta {} para url {}".format(e, url))
                  self.errors.append([e, content[0], url])
                self.queue.task_done()

    q = queue.Queue()
    for url in addresses:
        q.put(url)

    q_out = queue.Queue()

    for worker_number in range(no_workers):
        worker = Worker(q, worker_number, q_out)
        worker.setDaemon(True)
        worker.start()

    p = Printer(q_out)
    p.setDaemon(True)
    p.start()

    q.join()
    q_out.join()


def append_to_file(response):
  pickle.dump(response, open_file)

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
  counter = 0
  for row in reader:
    data.append([row['permalink'], build_places_url(row['latitude'], row['longitude']), counter])
    counter += 1

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

perform_web_requests(worker_data, 5)

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


