import time
import pickle
from bs4 import BeautifulSoup
from google.cloud import storage
import sys
from tqdm import tqdm

worker_number = int(sys.argv[1]) #Numero de worker que esta ejecutando este código

bucket_name = "bdm-unlu"
responses_file_name = "responses_{}.pkl".format(worker_number)
responses_blob_path = "html_scrapper/{}".format(responses_file_name)

result_file_name = "parsed_result_{}.pkl".format(worker_number)
result_blob_path = "html_parser/{}".format(result_file_name)

error_file_name = "parsed_error_file_name_{}.pkl".format(worker_number)
error_blob_path = "html_parser/{}".format(error_file_name)

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(responses_blob_path)

with open(responses_file_name, 'wb') as f:
    with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
        storage_client.download_blob_to_file(blob, file_obj)

def process_result(result):
  dict_result = {}
  soup = BeautifulSoup(result, 'html.parser')
  div = soup.find_all("div", {"class":"ui-pdp-specs"})[0]
  table = div.find_all("div", {"class":"ui-pdp-specs__table"})[0]
  keys = table.find_all("th", {"class":"ui-pdp-specs__table__column-title"})
  values = table.find_all("span", {"class":"andes-table__column--value"})

  for pair in zip(keys, values):
    dict_result[pair[0].text] = pair[1].text
  return dict_result


open_file_read = open(responses_file_name, "rb")

raw_results_count = 0
processed_results = []
has_load = True

errors = []
error_count = 0

while has_load:    
  raw_results_count += 1
  print("Read {} results. Error count {}".format(raw_results_count, error_count))
  try:
    raw_result = pickle.load(open_file_read)
  except Exception as e:
    print(e)
    has_load = False
  
  if has_load:
    try:
      processed_results.append([raw_result[0], process_result(raw_result[1])])
    except Exception as e:
      error_count += 1 
      errors.append(raw_result[0])

open_file_read.close()

open_file_write = open(result_file_name, "wb")

pickle.dump(processed_results, open_file_write)

open_file_write.close()

blob = bucket.blob(result_blob_path)

blob.upload_from_filename(result_file_name)

##

open_file_write = open(error_file_name, "wb")

pickle.dump(errors, open_file_write)

open_file_write.close()

blob = bucket.blob(error_blob_path)

blob.upload_from_filename(error_file_name)


print("{} Permalinks with errors: {}".format(len(errors), errors))
