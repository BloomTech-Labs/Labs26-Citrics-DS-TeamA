from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query
from app.smart_upper_function import smart_upper
import pandas as pd
import plotly.express as px

router = APIRouter()


@router.get('/rent_viz/{cityname}')
async def viz(cityname: str):
    """
    Visualize city-level rental price estimates from
    [Apartment List](https://www.apartmentlist.com/research/category/data-rent-estimates) 📈

    ### Path Parameter
    `cityname`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`
    - Does not currently include functionality for including statecode; e.g. `Atlanta, GA`
    - **Special Examples:**
        - **FORT:** *Ft. Lauderdale* should be entered as `Fort Lauderdale` or `fort lauderdale`
        - **SAINT:** *St. Louis* should be entered as `St. Louis` or `st. louis`
        - **DC:** *Washington DC* should be entered as `Washington` or `washington`

    ### Response
    JSON string to render with [react-plotly.js](https://plotly.com/javascript/react/)
    """

    # Get the city's rental price from database
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

    df = pd.read_json(fetch_query(query, columns))

    # Input sanitization
    cityname = smart_upper(cityname)

    # Make a set of citynames in the rental price data
    citynames = set(x.city.to_list())

    # Raise HTTPException for unknown inputs
    if cityname not in citynames:
        raise HTTPException(
            status_code=404,
            detail=f'City name "{cityname}" not found!'
        )

    # Otherwise, extract statecode (for use in title)
    statecode = x[x.city == cityname]["state"].to_list()[0]

    # Get subset for cityname input
    subset = x[x.city == cityname]

    # Create visualization
    fig = px.bar(
        subset,
        x="bedroom_size",
        y="price_2020_08",
        title=f"Rental Price Estimates for {cityname}, {statecode}"
    )

    return fig.to_json()