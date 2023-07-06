import os
import base64
import asyncio
import aiohttp
import json
import pandas as pd
import hashlib
import pyarrow

from google.cloud import bigquery

# note that the api docs give the base url as one thing, and the user account gives it as another

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/src/autonomous-bit-391913-5ed29af63398.json"


def get_account_key(account_name: str) -> str:
    """Function to grab sensitive information. Assumes you've stored appropriate information in a .route folder in home directory.

    Params:
        account_name: takes X-Api-Key or password
    """

    with open(os.path.expanduser(f"~/.route/{account_name}"), encoding="utf-8") as file:
        key = file.read().rstrip("\n")
    return key


def hash_dict(input_dict):
    # Convert the dict to a string with sorted keys
    input_str = json.dumps(input_dict, sort_keys=True)

    # Create a hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the bytes of the string
    hash_object.update(input_str.encode())

    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()

    return hash_hex


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


async def make_api_call(session: aiohttp.ClientSession, frames: []) -> pd.DataFrame:
    """Given a session, and an array of frames (representing a campaign), this will make an api call to
    the route api with some hard-coded parameters, and return the result."""

    body = {
        "route_release_id": 46,
        "route_algorithm_version": 10.2,
        "algorithm_figures": ["reach", "average_frequency", "impacts"],
        "target_month": 8,
        "standard_dayparts": [1, 8],
        "total_weeks": "1",
        "spot_length": 10,
        "spot_break_length": 50,
        "frames": frames,
    }

    unique_identifier = hash_dict(body)

    base_url = "https://uat-routeapi.mediatel.co.uk/rest/process/standard"

    async with session.post(url=base_url, json=body) as response:
        if response.status == 200:
            data = await response.json()
            df = pd.json_normalize(data)
            df["UID"] = unique_identifier

            df.rename(
                columns={
                    "figures.impacts": "impacts",
                    "figures.impacts_pedestrian": "impacts_pedestrian",
                    "figures.impacts_vehicular": "impacts_vehicular",
                    "figures.reach": "reach",
                    "figures.average_frequency": "average_frequency",
                    "figures.rag_status": "rag_status",
                    "metrics.total_frames": "total_frames",
                    "metrics.total_actual_contacts": "total_actual_contacts",
                    "metrics.total_actual_respondents": "total_actual_respondents",
                },
                inplace=True,
            )
            to_be_floats = ["impacts", "reach", "average_frequency"]
            df[to_be_floats] = df[to_be_floats].astype(float)
            return df[
                [
                    "UID",
                    "target_month",
                    "demographic",
                    "granular_audience",
                    "impacts",
                    "reach",
                    "average_frequency",
                    "rag_status",
                    "total_frames",
                    "total_actual_contacts",
                    "total_actual_respondents",
                ]
            ]

        else:
            print(await response.text())


async def push_to_bigquery(client: bigquery.Client, data: pd.DataFrame, table_id: str):
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


async def process_frame(
    session: aiohttp.ClientSession, client: bigquery.Client, frame: list, table_id: str
):
    df_to_be_pushed = await make_api_call(session=session, frames=frame)
    await push_to_bigquery(client=client, data=df_to_be_pushed, table_id=table_id)


async def main(array_of_frames: list):
    client = bigquery.Client(project="bigquerytest-264314")

    headers = {
        "Authorization": make_authorization_header(
            password=get_account_key(account_name="password")
        ),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Api-Key": get_account_key(account_name="X-Api-Key"),
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for frame in array_of_frames:
            task = asyncio.create_task(
                process_frame(
                    session=session, client=client, frame=frame, table_id="task1_table"
                )
            )
            tasks.append(task)

        await asyncio.gather(*tasks)


def get_inputs(directory: str):
    all_frames = []

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        with open(file_path, "r") as f:
            frames = []
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                number = int(line)
                frames.append(number)

            all_frames.append(frames)

    return all_frames


asyncio.run(
    main(
        array_of_frames=get_inputs(
            "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/pt 1"
        )
    )
)
