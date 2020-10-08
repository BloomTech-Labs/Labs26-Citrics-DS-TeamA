from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query

import pandas as pd

router = APIRouter()


@router.get('/static/{city}_{statecode}')
async def static(city: str, statecode: str):
    """
    Static city-level data for 135 US cities. Dataset compiled of rental price estimates,
    walkscores, population, and most prevelant job industry for each city. 📈

    ## Path Parameters
    `city`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ## Response
    JSON string of various city statistics for 135 US Cities.
    """

    query = """
    SELECT *
    FROM static
    """

    columns = [
        "city",
        "state",
        "studio",
        "onebr",
        "twobr",
        "threebr",
        "fourbr",
        "walkscore",
        "population",
        "occ_title",
        "hourly_wage",
        "annual_wage"]

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
    match = df.loc[(df.city.str.contains(city)) &
                   (df.state.str.contains(statecode))]

    # Raise HTTPException for unknown inputs
    if len(match) < 1:
        raise HTTPException(
            status_code=404,
            detail=f'{city}, {statecode} not found or lacked enough data to be included here!')

    # DF to dictionary
    pairs = match.to_json(orient='records')

    return pairs
