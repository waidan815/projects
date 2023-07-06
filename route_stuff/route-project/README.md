
Part 1:
Read the campaign data from the Google Cloud bucket.
Call the Route API with the campaign data and the given specifications.
Insert the response data from the API into a BigQuery table.
Part 2:
Read the frame data for a single campaign from the Google Cloud bucket.
Call the Route API for each frame in the campaign every 15 minutes within a week.
Insert the response data from the API into a BigQuery table.


Background
Route provides audience data (people who pass and see) for OOH assets and campaigns. The data for which is used by the advertising industry to buy/sell space on the OOH advertising, they do this both at an individual spot level, somewhat akin to a TV spot, on digital screens and at a campaign level. A campaign for OOH is defined by a group of assets (frames) that are made available over a particular time period. These campaigns are typically run against the Route API to get information on the reach - the number of individuals seeing the campaign, the frequency - the number of time on average the campaign is seen and the impacts - the total number of times a campaign is seen.

Limitations
To ensure the Route API accords with rules provided by Route and the Benchmarking Reach algorithm and to ensure optimum performance is maintained, the following limitations are in place:

The Route API will not calculate reach based figures (reach, cover and average frequency) where schedules have a gap of a week or more (i.e. a week-on/week-off schedule) based on Mon–Sun as whole weeks.
Grouping by frame_id cannot be used for more than 10,000 frames in a single call
Grouping cannot be used for more than 100,000 frames in a single call.
Where campaign schedules contain duplicate frames the dates/dayparts cannot overlap.
The demographic array is limited to allowing a maximum of 30 demographics in a single call.
The maximum number of resulting items/nodes cannot exceed 20,000 e.g. for a call with 10,000 frames using "grouping" by frame_id results in 10,000 output items. If applying more than 2 demographics at a time this will exceed 20,000 output nodes.


should take these params, and hash the campaign array. 
to give a unique ID. Primary key. 

If I had more time...

Refactor script such that it downloaded a blob, then in memory used that as an api call, wouldn't ahve to bother to save it in an intermediary location.
Think more about the bigQuery table structure
    - have a primary key
    - maybe have some sort of link to frame as there's info for each frame like location etc in another table
write some logging
write some tests
put more error handling
some sort of re-try functionality