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
