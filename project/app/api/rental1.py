from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query

router = APIRouter()


@router.get("/rental/")
async def rental_prices():
    """
    City-level historic rental prices for 1 bedroom apartments from
    [Apartment List](https://www.apartmentlist.com/research/category/data-rent-estimates) 📈

    ## Response
    JSON string of current rental price estimates for more than 400
    U.S. cities.
    """

    query = """
    SELECT
        city,
        "state",
        bedroom_size,
        price_2020_08
    FROM rp_clean1
    WHERE bedroom_size = '1br' OR bedroom_size = 'Studio'
    """

    columns = ["city", "state", "bedroom_size", "price_2020_08"]

    return fetch_query(query, columns)
