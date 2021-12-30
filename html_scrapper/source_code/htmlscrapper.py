import requests
import time
import pickle
import sys
import csv
from google.cloud import storage
from bs4 import BeautifulSoup

# Caso 1. Se hizo la petición, 200OK, Tenia spec table.
# Caso 2. Se hizo la petición, 200OK, No tenía spec table, tenía botón ver más, se consultó al anchor, y tenía spec table.
# Caso 3. Se hizo la petición, 200OK, No tenía spec table, tenía botón ver más, se consultó al anchor, y no tenía spec table.
# Caso 4. Se hizo la petición, 200OK, No tenía spec table, ni botón ver más.
# Caso 5. Error code != a 200OK

# Caso 4: Podría ser un error de red, de la API, desafío javascript, etc.

def effectuate_request(permalink):
  r = requests.get(permalink)
  if r.status_code == 200:
    if contains_specs_table(r.text):
      return [1, r.text]
    see_more_link = get_link_see_more_anchor(r.text)
    if see_more_link != None:
        response = effectuate_request(see_more_link)
        if response[0] == 1:
          return [2, response[1]]
        else:
          return [3, None]
    else:
      return [4, None]
  else:
    return [5, None]

def do_request(permalink):
  response_code, response_text = effectuate_request(permalink)
  if response_code == 1:
    append_to_file(permalink, response_text)
  if response_code == 2:
    append_to_file(permalink, response_text)


  error_text = ""
  if response_code == 3:
    error_text = "Permalink with see more link, couldn't be processed {}".format(permalink)
  if response_code == 4:
    error_text = "Permalink without see more link or spec table {}".format(permalink)
  if response_code == 5:
    error_text = "Permalink without a 200OK status code HTTP {}".format(permalink)

  if response_code == 3 or response_code == 4 or response_code == 5:
    time.sleep(0.005)
    response_code, response_text = effectuate_request(permalink)
    if response_code == 1 or response_code == 2:
      append_to_file(permalink, response_text)
    else:
      print("Re-Try didnt work. Error: {}".format(error_text))

## Funciones de la request
def get_link_see_more_anchor(request_text):
  try:
    soup = BeautifulSoup(request_text, 'html.parser')
    anchor = soup.find_all("a", {"class":"andes-button ui-search-billboard__action-button andes-button--medium andes-button--loud"})[0]
    result = anchor["href"]
  except Exception as e:
    result = None
  return result

def contains_specs_table(request_text):
  try:
    soup = BeautifulSoup(request_text, 'html.parser')
    div = soup.find_all("div", {"class":"ui-pdp-specs"})[0]
    table = div.find_all("div", {"class":"ui-pdp-specs__table"})[0]
    result = True
  except Exception as e:
    result = False
  return result

## Funciones para guardar el trabajo de los workers
def append_to_file(permalink, response):
  pickle.dump([permalink, response], open_file)


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

permalinks_with_errors = []

requests_done = 0
error_count = 0

for permalink in permalinks_worker:
  try:
    do_request(permalink)
  except Exception as e:
    print("Error: Exception {}".format(e))
  time.sleep(0.005)

print("permalinks_with_errors: {}".format(permalinks_with_errors))
  
open_file.close()
  
blob = bucket.blob(responses_blob_path)

blob.upload_from_filename(responses_file_name)



