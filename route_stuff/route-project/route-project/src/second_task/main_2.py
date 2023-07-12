import os
import base64
import asyncio
import aiohttp
import json
import pandas as pd
import hashlib
import pyarrow
import datetime
import time
import aiolimiter
import logging

from google.cloud import bigquery
from google.api_core.exceptions import NotFound, Forbidden, GoogleAPICallError
from aiohttp import ClientResponseError, ClientConnectionError, ClientPayloadError


logger = logging.getLogger(__name__)
# Create a file handler and set the log level to ERROR
handler = logging.FileHandler(
    "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/log.txt"
)
handler.setLevel(logging.INFO)
# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)
logger.error("Starting the Program!")


def get_account_key(account_name: str) -> str:
    """Function to grab sensitive information. Assumes you've stored appropriate information in a .route folder in home directory.

    Params:
        account_name: takes X-Api-Key or password
    """

    with open(os.path.expanduser(f"~/.route/{account_name}"), encoding="utf-8") as file:
        key = file.read().rstrip("\n")
    return key


def hash_dict(input_dict: dict) -> str:
    """Function to hash some input, so as to provide a unique identifier later"""

    input_str = json.dumps(input_dict, sort_keys=True)

    hash_object = hashlib.sha256()
    hash_object.update(input_str.encode())
    hash_hex = hash_object.hexdigest()

    return hash_hex


def get_data():
    frames = []
    with open(
        "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/pt 2/task_two.txt",
        "r",
    ) as f:
        lines = f.readlines()

        for line in lines:
            frames.append(int(line.strip()))
    return frames


def get_dates(start_date, end_date):
    current_datetime = start_date

    # Loop until the current datetime reaches the end date
    while current_datetime < end_date:
        # Define the start and end of the 15-minute interval
        datetime_from = current_datetime
        datetime_until = datetime_from + datetime.timedelta(minutes=15)

        # Yield the interval as a tuple
        yield (
            datetime_from.strftime("%Y-%m-%d %H:%M"),
            datetime_until.strftime("%Y-%m-%d %H:%M"),
        )

        # Move to the next 15-minute interval
        current_datetime = datetime_until


def make_authorization_header(
    password: str,
    username: str = "trial-three@route.org.uk",
) -> str:
    """Function to create an authorization header, for use in the API.
    Copied code from https://gist.github.com/brandonmwest/a2632d0a65088a20c00a.

    Params:
        username
        password
    """

    base64string = (
        base64.encodebytes(("%s:%s" % (username, password)).encode("utf8"))
        .decode("utf8")
        .replace("\n", "")
    )

    header = "Basic %s" % base64string
    return header


def split_into_chunks(arr, max_chunk_size):
    num_chunks = len(arr) // max_chunk_size
    if len(arr) % max_chunk_size != 0:
        num_chunks += 1

    chunk_size = len(arr) // num_chunks
    remainder = len(arr) % num_chunks

    chunks = []
    for i in range(num_chunks):
        if remainder > 0:
            chunk_start = i * chunk_size + min(i, remainder)
            chunk_end = chunk_start + chunk_size + 1
            remainder -= 1
        else:
            chunk_start = i * chunk_size + min(i, remainder)
            chunk_end = chunk_start + chunk_size
        chunks.append(arr[chunk_start:chunk_end])

    return chunks


async def make_custom_api_call(
    session: aiohttp.ClientSession,
    frames: [],
    datetime_from: datetime,
    datetime_until: datetime,
    rate_limiter: aiolimiter.AsyncLimiter,
) -> pd.DataFrame:
    """Given a session, and an array of frames (representing a campaign), this will make an api call to
    the route api with some hard-coded parameters, and return the result."""

    body = {
        "route_release_id": 46,
        "route_algorithm_version": 10.2,
        "algorithm_figures": ["impacts", "population"],
        "target_month": 8,
        "grouping": "frame_id",
        "campaign": [
            {
                "schedule": [
                    {
                        "datetime_from": datetime_from,
                        "datetime_until": datetime_until,
                    }
                ],
                "spot_length": 10,
                "spot_break_length": 50,
                "frames": frames,
            }
        ],
    }

    # unique_identifier = hash_dict(body)

    base_url = "https://uat-routeapi.mediatel.co.uk/rest/process/custom"
    async with rate_limiter:
        try:
            async with session.post(url=base_url, json=body) as response:
                if response.status == 200:
                    data = await response.json()
                    data["datefrom"], data["dateuntil"] = datetime_from, datetime_until
                    return data

                else:
                    logger.warning((await response.text()))

        except asyncio.TimeoutError as e:
            logger.error(f"Connection timed out, {e}")

        except ClientResponseError as e:
            logger.error(
                f"HTTP request failed, status: {e.status}, message: {e.message}"
            )

        except ClientConnectionError as e:
            logger.error(f"Network connection error: {e}")

        except ClientPayloadError as e:
            logger.error(f"Failed to read or decode payload: {e}")

        except Exception as e:
            logger.error(
                f"Unexpected error: {e} for Frames {frames[:5]} for Timespan {datetime_from}:{datetime_until}"
            )


def push_to_bigquery(client: bigquery.Client, data: pd.DataFrame, table_id: str):
    """Given a client, some data and a table name, will attempt to create a table within a dataset
    if one isn't found. If one is found, will push data to it"""

    dataset_id = "bigquerytest-264314.Release46_CandidateTest"

    try:
        tables = list(client.list_tables(dataset_id))
    except NotFound:
        logger.error(f"The dataset {dataset_id} does not exist.")
        return
    except Forbidden:
        logger.error("You do not have sufficient permissions to list the tables.")
        return
    except GoogleAPICallError as e:
        logger.error(f"An error occurred: {e}")
        return

    schema = [
        bigquery.SchemaField("demographic", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("granular_audience", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("target_month", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("frame_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("datetimefrom", "DATETIME", mode="REQUIRED"),
        bigquery.SchemaField("datetimeuntil", "DATETIME", mode="REQUIRED"),
        bigquery.SchemaField("population", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("impacts", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("impacts_pedestrian", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("impacts_vehicular", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("rag_status", "STRING", mode="REQUIRED"),
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
    try:
        job_config = bigquery.LoadJobConfig()
        job_config.schema = schema
        job_config.source_format = bigquery.SourceFormat.PARQUET
        job = client.load_table_from_dataframe(
            data, full_table_id, job_config=job_config
        )
        logger.info(f"Pushed: {data.head(1)} to BigQuery.")
        job.result()  # Wait for the job to complete
    except GoogleAPICallError as e:
        logger.error(f"An error occurred when pushing data to the table: {e}")


async def main(
    frames: [], date_from: datetime.datetime, date_until: datetime.datetime
) -> None:
    client = bigquery.Client(project="bigquerytest-264314")

    list_of_dataframes = []

    headers = {
        "Authorization": make_authorization_header(
            password=get_account_key(account_name="password")
        ),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Api-Key": get_account_key(account_name="X-Api-Key"),
    }

    timeout = aiohttp.ClientTimeout()

    limiter = aiolimiter.AsyncLimiter(1, 2)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        chunks = split_into_chunks(frames, 100)

        for chunk in chunks:
            tasks = []
            for date_from, date_until in get_dates(
                start_date=start_date, end_date=end_date
            ):
                task = asyncio.create_task(
                    make_custom_api_call(
                        session=session,
                        frames=chunk,
                        datetime_from=date_from,
                        datetime_until=date_until,
                        rate_limiter=limiter,
                    )
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            dataframes = []

            for json in responses:
                if "results" in json and isinstance(json["results"], list):
                    for result in json["results"]:
                        # Only consider 'grouping' results
                        if result["description"] == "grouping":
                            result["datetimefrom"] = json["datefrom"]
                            result["datetimeuntil"] = json["dateuntil"]

                            df = pd.json_normalize(result)  # flatten 'grouping' dict
                            dataframes.append(df)

            chunk_df = pd.concat(dataframes)
            chunk_df.rename(
                columns={
                    "figures.population": "population",
                    "figures.impacts": "impacts",
                    "figures.impacts_pedestrian": "impacts_pedestrian",
                    "figures.impacts_vehicular": "impacts_vehicular",
                    "figures.rag_status": "rag_status",
                },
                inplace=True,
            )
            to_be_floats = [
                "population",
                "impacts",
                "impacts_pedestrian",
                "impacts_vehicular",
            ]
            to_be_ints = ["frame_id", "target_month"]
            chunk_df[to_be_ints] = chunk_df[to_be_ints].astype(int)
            chunk_df[to_be_floats] = chunk_df[to_be_floats].astype(float)
            chunk_df["datetimefrom"] = pd.to_datetime(chunk_df["datetimefrom"])
            chunk_df["datetimeuntil"] = pd.to_datetime(chunk_df["datetimeuntil"])

            chunk_df = chunk_df[
                [
                    "demographic",
                    "granular_audience",
                    "target_month",
                    "frame_id",
                    "datetimefrom",
                    "datetimeuntil",
                    "population",
                    "impacts",
                    "impacts_pedestrian",
                    "impacts_vehicular",
                    "rag_status",
                ]
            ]
            print(chunk_df)
            # chunk_df.to_csv("lookatmc.csv")

            push_to_bigquery(client=client, data=chunk_df, table_id="task2_table")


frames = get_data()

start_date = datetime.datetime(2022, 8, 3, 0, 0, 0)
end_date = datetime.datetime(2022, 8, 7, 0, 0, 0)


asyncio.run(main(frames=frames, date_from=start_date, date_until=end_date))
