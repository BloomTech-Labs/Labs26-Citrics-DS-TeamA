from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query
from app.smart_upper_function import smart_upper
import pandas as pd
import plotly.express as px

router = APIRouter()


@router.get('/rent_viz_dep/{city}_{statecode}')
async def viz(city: str, statecode: str):
    """
    # (DEPRECATED)
    
    Visualize city-level **Studio** and **1-Bedroom** rental price estimates from
    [Apartment List](https://www.apartmentlist.com/research/category/data-rent-estimates) 📈

    ## Path Parameters
    `city`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`
    - **Special Examples:**
        - **DC:** *Washington DC* should be entered as `Washington` or `washington`

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ## Response
    - JSON string to render with [react-plotly.js](https://plotly.com/javascript/react/)

    - Lambda-specific docs for JSON string viz rendering available [here](https://github.com/Lambda-School-Labs/labs-spa-starter/tree/main/src/components/pages/ExampleDataViz)
    """

    # Get the city's rental price from database
    query = """
    SELECT
        city,
        "state",
        bedroom_size,
        price_2020_08
    FROM rp_clean1
    """

    columns = ["city", "state", "bedroom_size", "price_2020_08"]

    df = pd.read_json(fetch_query(query, columns))

    # Input sanitization
    city = smart_upper(city)
    statecode = statecode.lower().upper()

    # Make a set of citys in the rental price data
    citynames = set(df.city.to_list())
    statecodes = set(df.state.to_list())

    # Handle Edge Cases:
    ### saint
    if city[0:5] == "Saint":
        city = city.replace("Saint","St.")

    elif city[0:3] == "St ":
        city = city.replace("St","St.")

    ### fort
    elif city[0:3] == "Ft ":
        city = city.replace("Ft","Fort")

    elif city[0:3] == "Ft.":
        city = city.replace("Ft.","Fort")

    # Raise HTTPException for unknown inputs
    if city not in citynames:
        raise HTTPException(
            status_code=404,
            detail=f'City name "{city}" not found!'
        )

    if statecode not in statecodes:
        raise HTTPException(
            status_code=404,
            detail=f'State code "{statecode}" not found!'
        )

    # Get subset for city input
    subset = df[df.city == city]

    # Create visualization
    fig = px.bar(
        subset,
        x="price_2020_08",
        y="bedroom_size",
        title=f"Rental Price Estimates for {city}, {statecode}",
        orientation="h",
        template="ggplot2+xgridoff+ygridoff",
        color="price_2020_08",
        hover_data=["city", "state", "bedroom_size", "price_2020_08"],
        labels={
            "price_2020_08": "Rental Price Estimate",
            "bedroom_size": "Number of Bedrooms"
        },
        barmode="relative"
    )

    fig.update_layout(
        font=dict(
            family="trebuchet ms",
            color="darkslateblue",
            size=18
        ),
        width=500,
        height=500
    )

    return fig.to_json()
