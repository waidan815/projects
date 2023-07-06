import os
import base64
import asyncio
import aiohttp
import json
import pandas as pd
import hashlib
import pyarrow

from google.cloud import bigquery


async def push_to_bigquery(client: bigquery.Client, data: pd.DataFrame, table_id: str):
    """Given a client, some data and a table name, will attempt to create a table within a dataset
    if one isn't found. If one is found, will push data to it"""

    dataset_id = "bigquerytest-264314.Release46_CandidateTest"
    tables = list(client.list_tables("bigquerytest-264314.Release46_CandidateTest"))

    schema = [
        bigquery.SchemaField("UID", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("target_month", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("demographic", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("granular_audience", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("impacts", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("reach", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("average_frequency", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("rag_status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("total_frames", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_actual_contacts", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_actual_respondents", "INTEGER", mode="REQUIRED"),
    ]

    full_table_id = f"{dataset_id}.{table_id}"

    if table_id not in [table.table_id for table in tables]:
        # Create a new table
        table = bigquery.Table(full_table_id, schema=schema)
        table = client.create_table(table)
        print(
            "Created table {}.{}.{}".format(
                table.project, table.dataset_id, table.table_id
            )
        )

    job = client.load_table_from_dataframe(data, full_table_id)
    job.result()  # Wait for the job to complete
