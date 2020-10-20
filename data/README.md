# Data Sourcing

## Limitations of Current Deployment

It should be noted that the bulk of the data actually used in the project has been taken from datasets in the form of static *.csv* files. The API is, therefore, outdated. In order to update this, the **Labs 28 DS Team** will need to discover a way using APIs to periodically update these data. In some cases, as with the [**Bureau of Labor Statistics**](https://www.bls.gov/developers/) and [**Census**](https://www.census.gov/data/developers.html) data, the datasets used herein are periodically updated and accessible via their respective APIs.

With dynamic data, however, we introduce greater complexity, especially with regard to **time series** modeling. One approach would be to treat each table or column in **PostgreSQL** database as a something of a *queue* or *ring-buffer*; wherein old information is periodically discarded and new information is periodically inserted into the appropriate tables, ensuring *up-to-date predictions*, rather than stale ones based on old data.