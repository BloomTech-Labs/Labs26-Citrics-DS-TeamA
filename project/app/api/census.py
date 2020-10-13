from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query

import pandas as pd

router = APIRouter()


@router.get('/census/{city}_{statecode}')
async def census(city: str, statecode: str):
    """
    Population data (city-level) from
    [US Census Bureau](https://www.census.gov/data/tables/time-series/demo/popest/2010s-total-cities-and-towns.html) 📈

    ## Path Parameters
    `city`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ## Response
    JSON string of city population stats for more than 500
    U.S. cities.
    """

    query = """
    SELECT
        city,
        state,
        popestimate2019
    FROM census
    """

    columns = [
        "city",
        "state",
        "popestimate2019"]

    df = pd.read_json(fetch_query(query, columns))

    # Input sanitization
    city = city.title()
    statecode = statecode.lower().upper()

    # Handle Edge Cases:
    # saint
    if city[0:5] == "Saint":
        city = city.replace("Saint", "St.")

    elif city[0:3] == "St ":
        city = city.replace("St", "St.")

    # fort
    elif city[0:3] == "Ft ":
        city = city.replace("Ft", "Fort")

    elif city[0:3] == "Ft.":
        city = city.replace("Ft.", "Fort")

    # Find matching metro-area in database
    match = df.loc[(df.city.str.startswith(city)) &
                   (df.state.str.contains(statecode))].head(1)

    # Raise HTTPException for unknown inputs
    if len(match) < 1:
        raise HTTPException(
            status_code=404,
            detail=f'{city}, {statecode} not found!')

    # DF to dictionary
    pairs = match.to_json(orient='records')

    return pairs
