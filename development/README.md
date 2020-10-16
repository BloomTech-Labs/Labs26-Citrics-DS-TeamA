# Development Directory

## Purpose

The development directory is designed to store
- 1. Utilities which are used in deployment, consuming API data, and database management which are not used directly by the API itself.
- 2. Notebooks in which Exploratory and Explanatory Data Analyses are performed and the logic of routes are tested before they are deployed in the API.
- 3. Pre-routes <- Python Scripts which fill much of the same function as the notebooks, namely for testing the logic of a given route before it is incorporated into the API. These may seem superfluous, but given that Windows users tend to have more issues with Docker, it may be useful to test them out locally without a `docker-compose` first.