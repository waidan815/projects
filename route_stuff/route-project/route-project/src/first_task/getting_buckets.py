import os
from google.cloud import storage

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/awestcc/Documents/projects/projects/autonomous-bit-391913-5ed29af63398.json"


def list_blobs(bucket_name: str, storage_client: storage.client) -> list:
    """Lists all the blobs in the bucket."""

    blobs = storage_client.list_blobs(bucket_name)
    blob_names = []
    for blob in blobs:
        blob_names.append(blob.name)

    return blob_names


def download_blob(
    bucket_name: str,
    source_blob_name: str,
    destination_file_name: str,
    storage_client: storage.client,
):
    """Downloads a blob from the bucket."""

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def getting_bucket_data(
    bucket_name: str, local_dir: str, storage_client: storage.client
):
    """Function to download the data from the buckets to a local directory.
    Given a path to a folder, will attempt to make one if one doesn't
    already exist. Then, will download each blob in the bucket, and save to
    that folder.

    (GCP buckets has a flat file structure, so we have to filter to get the ones
    we want. Atm this is pretty hacky just with a .startswith)."""

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
