"""main point of execution."""

import os
from google.cloud import storage

import os
from google.cloud import storage


os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/src/autonomous-bit-391913-5ed29af63398.json"

# Now you can use the storage client
storage_client = storage.Client(project="bigquerytest-264314")

# And so on...


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client(project="bigquerytest-264314")
    blobs = storage_client.list_blobs(bucket_name)
    blob_names = []
    for blob in blobs:
        blob_names.append(blob.name)

    return blob_names


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client(project="bigquerytest-264314")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    # print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


def main(bucket_name, local_dir):
    # List all files in the bucket
    blobs = list_blobs(bucket_name)

    os.makedirs(
        local_dir,
        exist_ok=True,
    )

    # Download all files to a local directory
    for blob_name in blobs:
        if blob_name.startswith("pt 1"):
            source_blob_name = blob_name
            destination_file_name = os.path.join(local_dir, blob_name)

            download_blob(bucket_name, source_blob_name, destination_file_name)


main(
    bucket_name="routedata_r46_schedules",
    local_dir="/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/pt 1",
)
