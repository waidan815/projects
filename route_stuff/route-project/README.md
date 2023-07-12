
### Overview of Module

    results/ 
        - all the google bucket files are stored here

    main - point of entry

    src/
      first task/
        calling api = all the api functions
        getting buckets = all the functions to get data from GCP buckets
        helpful functions = a couple of functions to test things / delete unwanted files
        pushing to bigquery = functions to help push to bq

      second_task/
        api_call.py

    tests/  = empty tests folder

    poetry.lock = contains exact version of dependencies
    pyproject.toml = config file storing dependencies
    readme.md
### To run
It's not quite set up to run from anywhere, as a lot of the paths are hard coded. 
However, assuming they're all fine, you've got the necessary credentials on your 
machine (GCLI creds, api keys, auth logins etc)

`pip install poetry` if you haven't already. 
`cd` to the directory level with the toml file. 
`poetry install` to install dependencies
`poetry shell` to create a VM
then you can `python main.py` inside that shell to run the script

### Task 1
- Authenticates using google CLI. 
- This grabs some data from buckets, uses it to call the api and stores the results in a bigquery table. 
- Api calls are written such that they are executed concurrently. 
- Hashing. Looking into it further, BigQuery doesn't implement primary keys in the same way that other DBs (i.e.
  postgres) does, so hashing the input wasn't strictly necessary here.

### Task 2
- This is a much more involved task, as we have to make lots more calls. For every frame (~ 14,000), for every 15-min interval
  within a week, we need to call the API. Can call with an array of lots of frames, and then group by frame. So, we'll get a
  separate dictionary for each frame, for every 15 min interval within the week. 
- So, need to make 672 ((60mins is one hour *  24 hours in a day * 7 days in a week) / 15 minute intervals) calls to the API. 
- Although, the grouping only supports 10,000 frames maximum, so will need to chunk the array up into suitable chunks. 

- I had a dive into best practices for BQ, ideally, we'd have some sort of pipeline where:
  - for each chunk, call the api ~672 times. 
  - store the output of that as some sort of compressed (i.e. parquet) file locally. 
  - then upload that to google buckets
  - then transfer across to bigquery. 
  - if necessary, clean up local storage and buckets

- However, as upload access to buckets is restricted here, and implementation time is limited, I'm skipping the intermediary stages.
  So, my pipeline is much simpler:
  - for each chunk, call the api.
  - push the output of that api call to bigquery. 
  - it is a slight upgrade to task 1 in that it aggregates a large number of calls into one pandas dataframe, then batch pushes to BigQuery. 

  
- As such, the process is not very fault-tolerant. If something goes wrong, it's not the simplest thing to pick up from where the 
  program left off. 
- This is somewhat countered by the logging & error handling but not completely. 
- Talking of fault-tolerant, I wasn't able to discern the actual rate limits on the UAT api, so I've used a 3rd party library to limit
  the number of calls per second. This probably makes the program slower than it needs to be, but thought I'd err on the side of caution.


### Automating fully. 
- Following up on our talk on automation last week, I had a look into how to take this program to the next level. 

- As these two tasks do 2 different (slightly) things, it would make sense to have them running as different services. As the data is going 
  from Buckets to BigQuery, it makes sense to stay within GCP. From looking into this a bit, there would be 3 options to take this to the 
  next step, all of which would require containerization of the program. (not hard to do, just would have had to re-write env variables, file
  paths, api keys etc.)

  1 - Google Compute Engine, essentially just a VM where you pay for size of machine provisioned
  2 - Google Cloud Run, runs application in stateless containers, where you pay for exact usage / compute needed
  3 - Google K8s, but would probably be overkill for simple application like this. 

  Google Cloud Run makes the most sense. 
