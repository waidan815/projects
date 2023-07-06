"""Main point of execution."""

import os

from google.cloud import storage

import first_task.getting_buckets
import first_task.calling_api
import first_task.helpful_functions
import first_task.pushing_to_bq


os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/awestcc/Documents/projects/projects/autonomous-bit-391913-5ed29af63398.json"


def buckets():
    storage_client = storage.Client(project="bigquerytest-264314")

    getting_bucket_data(
        bucket_name="routedata_r46_schedules",
        local_dir="/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/pt 1",
        storage_client=storage_client,
    )


async def process_frame(
    session: aiohttp.ClientSession, client: bigquery.Client, frame: list, table_id: str
):
    """Helper function to maintain synchronous nature of pulling data from api and pushing to bq"""
    df_to_be_pushed = await make_api_call(session=session, frames=frame)
    await push_to_bigquery(client=client, data=df_to_be_pushed, table_id=table_id)


async def main(array_of_frames: list):
    """Main point of entry to the script. Initializes the session, creates tasks and gathers them all into one future."""
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


asyncio.run(
    main(
        array_of_frames=get_inputs(
            "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/results/pt 1"
        )
    )
)
