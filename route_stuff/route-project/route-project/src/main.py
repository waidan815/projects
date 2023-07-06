"""Main point of execution."""

import os

from google.cloud import storage

import first_task.getting_buckets


def main():
    storage_client = storage.Client(project="bigquerytest-264314")

    getting_bucket_data(
        bucket_name="routedata_r46_schedules",
        local_dir="/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/pt 1",
        storage_client=storage_client,
    )
