import os
import base64
import asyncio
import aiohttp
import json
import pandas as pd
import hashlib
import pyarrow
import datetime


from google.cloud import bigquery

# for every frame (int) within a campaign (array of ints)
# call the api to get the audience.
# ig using
# """- Target month of August
# - Route release 46
# - Algorithm version 10.2
# - target demographic : All Adults
# - spot length of 10 seconds
# - break length of 50 seconds"""
# as params


# so can group by frame ID, or by time (only by daypart). Need to make about 700 slots. Have 14,000 frames.

# so have to split it into two frames.

# Grouping by frame_id cannot be used for more than 10,000 frames in a single call
# Grouping cannot be used for more than 100,000 frames in a single call.

# note that the api docs give the base url as one thing, and the user account gives it as another


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


async def make_custom_api_call(
    session: aiohttp.ClientSession,
    frames: [],
    datetime_from: datetime,
    datetime_until: datetime,
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

    async with session.post(url=base_url, json=body) as response:
        if response.status == 200:
            data = await response.json()
            return data

            # df = pd.json_normalize(data)
            # df["UID"] = unique_identifier

            # df.rename(
            #     columns={
            #         "figures.impacts": "impacts",
            #         "figures.impacts_pedestrian": "impacts_pedestrian",
            #         "figures.impacts_vehicular": "impacts_vehicular",
            #         "figures.reach": "reach",
            #         "figures.average_frequency": "average_frequency",
            #         "figures.rag_status": "rag_status",
            #         "metrics.total_frames": "total_frames",
            #         "metrics.total_actual_contacts": "total_actual_contacts",
            #         "metrics.total_actual_respondents": "total_actual_respondents",
            #     },
            #     inplace=True,
            # )
            # to_be_floats = ["impacts", "reach", "average_frequency"]
            # df[to_be_floats] = df[to_be_floats].astype(float)
            # return df[
            #     [
            #         "UID",
            #         "target_month",
            #         "demographic",
            #         "granular_audience",
            #         "impacts",
            #         "reach",
            #         "average_frequency",
            #         "rag_status",
            #         "total_frames",
            #         "total_actual_contacts",
            #         "total_actual_respondents",
            #     ]
            # ]

        else:
            print(await response.text())


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


frames = get_data()


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


# Usage example:


async def main(frames):
    headers = {
        "Authorization": make_authorization_header(
            password=get_account_key(account_name="password")
        ),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Api-Key": get_account_key(account_name="X-Api-Key"),
    }
    start_date = datetime.datetime(2022, 8, 1)
    end_date = datetime.datetime(2022, 8, 2)

    async with aiohttp.ClientSession(headers=headers) as session:
        chunks = split_into_chunks(frames, 100)

        first_10 = chunks[0][:10]
        print(first_10)

        for date_from, date_until in get_dates(
            start_date=start_date, end_date=end_date
        ):
            res = await make_custom_api_call(
                session=session,
                frames=first_10,
                datetime_from=date_from,
                datetime_until=date_until,
            )

            print(res)
            print(len(res))

            break


asyncio.run(main(frames=frames))
