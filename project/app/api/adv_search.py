from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query

import pandas as pd

router = APIRouter()


@router.get('/adv_search/{popmin}_{br_size}_{max_rent}_{climate}')
async def adv_search(
    popmin: int, 
    br_size: int, 
    max_rent: int, 
    climate: str, 
    popmax=50_000_000
    ):
    """
    Advanced search function which locates matching cities based on specified
    criteria.

    ## Path Parameters
    `popmin`: The minimum desired population size; e.g. `0` or `75000`

    `popmax`: (Optional) The maximum desired population size; e.g. `699999`

    `br_size`: The number of bedrooms for which `max_rent` will be applied; e.g. `0` for studio,
    `4` for four bedrooms

    `max_rent`: The maximum rent amount for corresponding `br_size`; e.g. `1500` or `2500`

    `climate`: The preferred climate; e.g. `cold`, `mild`, or `hot`

    ## Response
    JSON string of all matching cities per specified criteria.
    """

    if br_size == 0:
        br_size = "studio"
    elif br_size == 1:
        br_size = "onebr"
    elif br_size == 2:
        br_size = "twobr"
    elif br_size == 3:
        br_size = "threebr"
    elif br_size == 4:
        br_size = "fourbr"

    query = f"""
    SELECT *
    FROM "static"
    WHERE population >= {popmin} AND population <= {popmax}
    AND {br_size} <= {max_rent}
    AND simple_climate='{climate}'
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
        "annual_wage",
        "climate_zone",
        "simple_climate"]

    df = pd.read_json(fetch_query(query, columns))

    # Input sanitization - will need different sanitization logic
    # city = city.title()
    # statecode = statecode.lower().upper()

    # Raise HTTPException if no matches found
    if len(df) < 1:
        raise HTTPException(
            status_code=404,
            detail=f'No cities found that match your criteria ... please try again!')

    # DF to dictionary
    pairs = df.to_json(orient='records')

    print("Number of Cities:", len(df))

    return pairs
