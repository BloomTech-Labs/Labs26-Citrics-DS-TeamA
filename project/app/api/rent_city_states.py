from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query

router = APIRouter()


@router.get("/rent_city_state/")
async def cities_and_states_for_frontend():
    """
    City-level historic rental prices for 1 bedroom apartments from
    [Apartment List](https://www.apartmentlist.com/research/category/data-rent-estimates) 📈

    ## Response
    JSON string of city names and statecodes found in the rental price data.
    """

    query = """
    SELECT
        city,
        "state"
    FROM rp_clean1
    WHERE bedroom_size = 'Studio'
    """

    columns = ["city", "state"]

    return fetch_query(query, columns)
