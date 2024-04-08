# from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import pandas as pd
from google.cloud import storage

# print(os.path.exists("C:\\Users\abhir\Downloads\stone-goal-401904-a74c6fec862f.json"))
credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
credentials_dict = json.load(open(r"C:\Users\abhir\Downloads\stone-goal-401904-364eb9bc2e42.json", "r"))
# credentials_dict = {
#     'type': 'service_account',
#     'client_id': os.environ['BACKUP_CLIENT_ID'],
#     'client_email': os.environ['BACKUP_CLIENT_EMAIL'],
#     'private_key_id': os.environ['BACKUP_PRIVATE_KEY_ID'],
#     'private_key': os.environ['BACKUP_PRIVATE_KEY'],
# }
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict
)
dst = r"C:\Python\data\etf_data"
# storage_client = storage.Client(credentials=credentials, project='stone-goal-401904')
# bucket = client.get_bucket('price-data-etf')
# for filename in os.listdir(dst):
#     blob = bucket.blob(f"price-data/{filename}")
#     filepath = dst + "/" + filename
#     blob.upload_from_filename(filepath)
# request = client.objects().list(bucket="price-data-etf", prefix = "price_data")
# data_bytes = blob.download_as_string()

# df = pd.read_excel(data_bytes)
# blob.upload_from_filename(r"C:\Python\Commercial_Dashboard\price_data_top5.xlsx")




"""
When interacting with Google Cloud Client libraries, the library can auto-detect the
credentials to use.

// TODO(Developer):
//  1. Before running this sample,
//  set up ADC as described in https://cloud.google.com/docs/authentication/external/set-up-adc
//  2. Replace the project variable.
//  3. Make sure that the user account or service account that you are using
//  has the required permissions. For this sample, you must have "storage.buckets.list".
Args:
    project_id: The project id of your Google Cloud project.
"""

    # This snippet demonstrates how to list buckets.
    # *NOTE*: Replace the client created below with the client required for your application.
    # Note that the credentials are not specified when constructing the client.
    # Hence, the client library will look for credentials using ADC.
storage_client = storage.Client(project="stone-goal-401904")
# storage_client = storage.Client.from_service_account_json(r"C:\Users\abhir\AppData\Roaming\gcloud\application_default_credentials.json")
bucket = storage_client.get_bucket("price-data-etf")

blobs = bucket.list_blobs()

for blob in blobs:
    print(blob.name)
# buckets = storage_client.list_buckets()
# print("Buckets:")
# for bucket in buckets:
#     print(bucket.name)
# print("Listed all storage buckets.")
a=2