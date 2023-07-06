from google.cloud import bigquery

# client = bigquery.client(project="bigquerytest-264314")

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/awestcc/Documents/projects/projects/route_stuff/route-project/route-project/src/autonomous-bit-391913-5ed29af63398.json"


dataset_id = "your_dataset"
table_id = "your_table"

table_ref = client.dataset(dataset_id).table(table_id)


def push_to_bigquery(data):
    rows_to_insert = [tuple(row.values()) for row in data]

    errors = client.insert_rows(table_ref, rows_to_insert)

    if errors:
        print(f"Errors occurred: {errors}")
    else:
        print("Rows were successfully inserted.")
