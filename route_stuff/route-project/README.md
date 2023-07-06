
### Overview of Module

    results/ 
        - all the google bucket files are stored here

    main - point of entry

    src/first task/
        calling api = all the api functions
        getting buckets = all the functions to get data from GCP buckets
        helpful functions = a couple of functions to test things / delete unwanted files
        pushing to bigquery = functions to help push to bq

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





### Design Decisions
- Authentication: GCP provides lots of methods for authentication, it would have been much better to 
  use a service account, as you have more flexibility over roles/ security etc. However, I couldn't do that so
  had to login through GCP CLI and get a json credentials file, which I then passed as an env variable.
- Asynchronous nature: As far as I could see, there were 3 bottlenecks to the process, which were the 3 I/O tasks.
  Although I wasn't sure how much stress this would put on the route API, I decided to write some async code that
  if it was waiting for a task to complete, could move onto the next task in the meantime. As such, each pull from 
  api and push to bq could happen concurrently (more or less.) 
- Hashing the input: Not much thought went into this one, I just wanted to have a unique column for each row that
  was pushed to bq. Hashing the data would allow me to check easily if it's already in the db. Maybe more something 
  for further down the line, and I appreciate that that wouldn't allow me to push multiple calls into the same table.
- Using pandas: Again not much thought. Went with a library I know to transform data such that it fit the schema. 
- Schema: Kept the things I thought could be useful. Would definitely spend more time on this part if I had to do this again

### If I had More Time...
Would definitely have made many changes.
Simple things:
    - logging
    - tests
    - much much more error handling
    - retry functionality / cool-off

More complex
    - refactored script so that it didn't bother saving blob to text file, but did everything in memory. 
    - thought more about the bq table structure, created a PK, included date of check, linked another table etc
    - split up larger functions into subfunctions. Makes it easier to test. E.g. api call & transformation. 
### Background
Route provides audience data (people who pass and see) for OOH assets and campaigns. The data for which is used by the advertising industry to buy/sell space on the OOH advertising, they do this both at an individual spot level, somewhat akin to a TV spot, on digital screens and at a campaign level. A campaign for OOH is defined by a group of assets (frames) that are made available over a particular time period. These campaigns are typically run against the Route API to get information on the reach - the number of individuals seeing the campaign, the frequency - the number of time on average the campaign is seen and the impacts - the total number of times a campaign is seen.

### Constraints

(putting constraints here so I can refer to them)
Limitations
To ensure the Route API accords with rules provided by Route and the Benchmarking Reach algorithm and to ensure optimum performance is maintained, the following limitations are in place:

The Route API will not calculate reach based figures (reach, cover and average frequency) where schedules have a gap of a week or more (i.e. a week-on/week-off schedule) based on Mon–Sun as whole weeks.
Grouping by frame_id cannot be used for more than 10,000 frames in a single call
Grouping cannot be used for more than 100,000 frames in a single call.
Where campaign schedules contain duplicate frames the dates/dayparts cannot overlap.
The demographic array is limited to allowing a maximum of 30 demographics in a single call.
The maximum number of resulting items/nodes cannot exceed 20,000 e.g. for a call with 10,000 frames using "grouping" by frame_id results in 10,000 output items. If applying more than 2 demographics at a time this will exceed 20,000 output nodes.



