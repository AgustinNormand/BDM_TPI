import base64

#
from google.cloud import pubsub_v1
from google.cloud import storage
import pandas as pd
import os
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error,  mean_absolute_error
from math import sqrt

def hello_pubsub(event, context):
	"""Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
	if not os.path.isfile("x_train.csv") or not os.path.isfile("y_train.csv") or not os.path.isfile("x_test.csv") or not os.path.isfile("y_test.csv"):
		storage_client = storage.Client()
		bucket = storage_client.bucket("bdm-unlu")
		blob = bucket.blob("21_train-test-split/x_train.csv")
		blob.download_to_filename("/tmp/x_train.csv")
		blob = bucket.blob("21_train-test-split/y_train.csv")
		blob.download_to_filename("/tmp/y_train.csv")
		blob = bucket.blob("21_train-test-split/x_test.csv")
		blob.download_to_filename("/tmp/x_test.csv")
		blob = bucket.blob("21_train-test-split/y_test.csv")
		blob.download_to_filename("/tmp/y_test.csv")

	x_train_original = pd.read_csv("/tmp/x_train.csv")

	x_test_original = pd.read_csv("/tmp/x_test.csv")

	decoded_message = json.loads(base64.b64decode(event['data']).decode('utf-8'))

	print(decoded_message)
	features = decoded_message["features"]
	print("Features: {}".format(features))
	grid = decoded_message["grid"]
	tree = grid["tree"]
	grid.pop("tree")
	print("Tree: {}".format(tree))
	print("Grid: {}".format(grid))
	x_train = x_train_original[features]
	x_test = x_test_original[features]

	if tree == ['RFRegressor']:
		decoded_message["results"] = rf_regressor(grid, x_test, x_train)

	encoded_message = json.dumps(decoded_message).encode('utf-8')

	topic_name = 'projects/{project_id}/topics/{topic}'.format(
		project_id="cryptic-opus-335323",
		topic='rf_results',
	)
	future = pubsub_v1.PublisherClient().publish(topic_name, encoded_message)
	future.result()

def rf_regressor(grid, x_test, x_train):
	y_train_original = pd.read_csv("/tmp/y_train.csv")
	y_test_original = pd.read_csv("/tmp/y_test.csv")
	rf = RandomForestRegressor(n_jobs=-1, verbose=2)
	rf_random = GridSearchCV(estimator = rf, param_grid = grid, cv = 5, verbose=2, n_jobs = -1)
	rf_random.fit(x_train, y_train_original)

	y_pred = rf_random.predict(x_test)

	results = {}
	mae = mean_absolute_error(y_test_original, y_pred)
	results["mae"] = mae
	mse = mean_squared_error(y_test_original, y_pred)
	results["mse"] = mse
	rmse = sqrt(mse)

	print('MAE: ', mae)
	print('MSE: ', mse)
	print("RMSE: ", rmse)

	results["rmse"] = rmse

	return results