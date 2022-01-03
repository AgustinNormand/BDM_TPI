import pickle
from bs4 import BeautifulSoup
from google.cloud import storage
import sys
import gzip
import difflib

worker_number = int(sys.argv[1]) #Numero de worker que esta ejecutando este código

bucket_name = "bdm-unlu"
responses_file_name = "responses_{}.pkl".format(worker_number)
responses_blob_path = "html_scrapper/{}".format(responses_file_name)

result_file_name = "parsed_result_{}.pkl".format(worker_number)
result_blob_path = "html_description_parser/{}".format(result_file_name)

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(responses_blob_path)

print("Downloading {}".format(responses_file_name))
blob.download_to_filename(responses_file_name)
print("File downloaded.")

def obtain_cleaned_description(result):
  soup = BeautifulSoup(result, 'html.parser')
  p = str(soup.find_all("p", {"class":"ui-pdp-description__content"})[0])
  cleaned_description = p.replace("\r", "") \
                       .replace("<br/>", "") \
                       .replace("<p class=\"ui-pdp-description__content\">", "") \
                       .replace("</p>", "") \
                       .upper() \
                       .split(" ")
  return cleaned_description

#def has_pool(cleaned_description):
#  has_pool = False

  
#  pileta_matches = difflib.get_close_matches('PILETA', cleaned_description, cutoff=0.8)
#  if len(pileta_matches) > 0:
#    has_pool = True
#  else:
#    piscina_matches = difflib.get_close_matches('PISCINA', cleaned_description, cutoff=0.8)
#    has_pool = len(piscina_matches) > 0
  
#  return has_pool

open_file_read = gzip.open(responses_file_name, 'rb')

raw_results_count = 0
processed_results = []
has_load = True

permalinks_with_errors = []
error_count = 0

while has_load:    
  raw_results_count += 1
  try:
    raw_result = pickle.load(open_file_read)
  except Exception as e:
    print(e)
    has_load = False
  
  if has_load:
    try:
      #cleaned_description = obtain_cleaned_description(raw_result[1])
      #processed_results.append([raw_result[0], has_pool(cleaned_description), cleaned_description])
      processed_results.append([raw_result[0], obtain_cleaned_description(raw_result[1])])
    except Exception as e:
      error_count += 1 
      print("Error: {}, Error count: {}".format(e, error_count))
      processed_results.append([raw_result[0], ""])
      permalinks_with_errors.append(raw_result[0])

open_file_read.close()

open_file_write = gzip.GzipFile(result_file_name, "wb")

pickle.dump(processed_results, open_file_write)

open_file_write.close()

blob = bucket.blob(result_blob_path)

blob.upload_from_filename(result_file_name)

##

print("{} Permalinks with errors: {}".format(len(permalinks_with_errors), permalinks_with_errors))
