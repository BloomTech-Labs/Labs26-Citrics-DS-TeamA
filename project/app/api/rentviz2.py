from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query
from app.smart_upper_function import smart_upper
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

router = APIRouter()


@router.get('/rent_viz2/{city}_{statecode}')
async def viz(city: str, statecode: str,
              city2: Optional[str]=None, statecode2: Optional[str]=None,
              city3: Optional[str]=None, statecode3: Optional[str]=None):
    """
    Visualize city-level rental price estimates from
    [Apartment List](https://www.apartmentlist.com/research/category/data-rent-estimates) 📈

    ## Path Parameters
    `city`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ## Query Parameters (Optional)
    `city2`: The name of a second US city to make rental comparison.

    `statecode2`: The statecode for second US city to make rental comparison.

    `city3`: The name of a third US city to make rental comparison.

    `statecode3`: The statecode for third US city to make rental comparison.

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

    # Make a set of cities in the rental price data
    citynames = set(df.city.to_list())
    statecodes = set(df.state.to_list())

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

    if city2 and statecode2:
        city2 = city2.title()
        statecode2 = statecode2.lower().upper()
        # saint
        if city2[0:5] == "Saint":
            city = city.replace("Saint", "St.")
        elif city2[0:3] == "St ":
            city2 = city2.replace("St", "St.")
        # fort
        elif city2[0:3] == "Ft ":
            city2 = city2.replace("Ft", "Fort")
        elif city2[0:3] == "Ft.":
            city2 = city2.replace("Ft.", "Fort")

    if city3 and statecode3:
        city3 = city3.title()
        statecode3 = statecode3.lower().upper()
        # saint
        if city3[0:5] == "Saint":
            city = city.replace("Saint", "St.")
        elif city3[0:3] == "St ":
            city3 = city3.replace("St", "St.")
        # fort
        elif city3[0:3] == "Ft ":
            city3 = city3.replace("Ft", "Fort")
        elif city3[0:3] == "Ft.":
            city3 = city3.replace("Ft.", "Fort")

    # Raise HTTPException for unknown inputs
    if city not in citynames:
        raise HTTPException(
            status_code=404,
            detail=f'City name "{city}" not found!'
        )
    if city2 not in citynames and city2:
        raise HTTPException(
            status_code=404,
            detail=f'City name "{city2}" not found!'
        )
    if city3 not in citynames and city3:
        raise HTTPException(
            status_code=404,
            detail=f'City name "{city3}" not found!'
        )

    if statecode not in statecodes:
        raise HTTPException(
            status_code=404,
            detail=f'Statecode "{statecode}" not found!'
        )
    if statecode2 not in statecodes and statecode2:
        raise HTTPException(
            status_code=404,
            detail=f'Statecode "{statecode2}" not found!'
        )
    if statecode3 not in statecodes and statecode3:
        raise HTTPException(
            status_code=404,
            detail=f'Statecode "{statecode3}" not found!'
        )

    # Get subset for city input
    city1_df = df[df.city == city]
    if city2 is not None:
        city2_df = df[df.city == city2]
    if city3:
        city3_df = df[df.city == city3]

     # Create empty dictionary to store styling data in.
    styling = dict()
    # If there's only one city (not a comparison)...
    if city and not city2 and not city3:
        styling['city1color'] = px.colors.sequential.Darkmint
        styling['title'] = f'Rental Price Estimates for {city}, {statecode}'
    # If there's a single city to compare to:
    if city and city2:
        # Make comparison of values (we can change this to .any() or .all())
        city1max = max(city1_df['price_2020_08'].values)
        city2max = max(city2_df['price_2020_08'].values)
        # If there's only 2 cities, make comparison / style.
        if city1max > city2max and not city3:
                styling['city1color'] = '#CC0000'  # red
                styling['city2color'] = '#4BB543'  # green
                styling['title'] = (f'{city}, {statecode} has higher rental ' +
                                    f'rates than {city2}, {statecode2}.')
        # Make comparison / style (opposite order).
        elif city1max < city2max and not city3:
                styling['city1color'] = '#4BB543'  # green
                styling['city2color'] = '#CC0000'  # red
                styling['title'] = (f'{city}, {statecode} has lower rental ' +
                                    f'rates than {city2}, {statecode2}.')
        # Check if there's 3 cities (max) to compare)
        if city and city2 and city3:
            city1max = max(city1_df['price_2020_08'].values)
            city2max = max(city2_df['price_2020_08'].values)
            city3max = max(city3_df['price_2020_08'].values)

            # POSSIBLE CONDITIONS:
            # 1 > 2 > 3
            # 1 > 3 > 2
            # 2 > 1 > 3
            # 2 > 3 > 1
            # 3 > 1 > 2
            # 3 > 2 > 1

            # Make comparison / style.
            if (city1max > city2max) and (city2max > city3max):
                # 1 > 2 > 3
                    styling['city1color'] = '#CC0000'  # red
                    styling['city2color'] = 'darkcyan'
                    styling['city3color'] = '#4BB543'  # green
                    styling['title'] = (f'{city}, {statecode} has higher rental rates ' +
                                        f'than {city2}, {statecode2} and {city3}, {statecode3}.')
            # Make comparison / style.
            elif (city1max > city3max) and (city3max > city2max):
                # 1 > 3 > 2
                    styling['city1color'] = '#CC0000'  # red
                    styling['city2color'] = '#4BB543'  # green
                    styling['city3color'] = 'darkcyan'
                    styling['title'] = (f'{city}, {statecode} has higher rental rates ' +
                                        f'than {city2}, {statecode2} and {city3}, {statecode3}.')
            # Make comparison / style.
            elif (city2max > city1max) and (city1max > city2max):
                # 2 > 1 > 3
                    styling['city1color'] = 'darkcyan'
                    styling['city2color'] = '#CC0000'  # red
                    styling['city3color'] = '#4BB543'  # green
                    styling['title'] = (f'{city}, {statecode} has higher rental rates ' +
                                        f'than {city3}, {statecode2}, but lower than {city2}, {statecode3}.')
            # Make comparison / style.
            elif (city2max > city3max) and (city3max > city1max):
                # 2 > 3 > 1
                    styling['city1color'] = '#4BB543'  # green
                    styling['city2color'] = '#CC0000'  # red
                    styling['city3color'] = 'darkcyan'
                    styling['title'] = (f'{city}, {statecode} has lower rental rates ' +
                                        f'than {city2}, {statecode2} and {city3}, {statecode3}.')
            # Make comparison / style.
            elif (city3max > city1max) and (city1max > city2max):
                # 3 > 1 > 2
                    styling['city1color'] = 'darkcyan'
                    styling['city2color'] = '#4BB543'  # green
                    styling['city3color'] = '#CC0000'  # red
                    styling['title'] = (f'{city}, {statecode} has higher rental rates ' +
                                        f'than {city2}, {statecode2}, but lower than {city3}, {statecode3}.')
            # Make comparison / style.
            elif (city3max > city2max) and (city2max > city1max):
                # 3 > 2 > 1
                    styling['city1color'] = '#4BB543'  # green
                    styling['city2color'] = 'darkcyan'
                    styling['city3color'] = '#CC0000'  # red
                    styling['title'] = (f'{city}, {statecode} has lower rental rates ' +
                                        f'than {city2}, {statecode2} and {city3}, {statecode3}.')
    # Create array; populate with bar data for first city.
    figure_data = [go.Bar(name=city,
                          x=city1_df['bedroom_size'],
                          y=city1_df['price_2020_08'],
                          marker_color=styling.get('city1color'))]

    # If city2 exists, append a bar for it.
    if city2:
        fig2_bar = go.Bar(name=city2,
                          x=city2_df['bedroom_size'],
                          y=city2_df['price_2020_08'],
                          marker_color=styling.get('city2color'))
        figure_data.append(fig2_bar)

    # If city3 exists, append a bar for it.
    if city3:
        fig3_bar = go.Bar(name=city3,
                          x=city3_df['bedroom_size'],
                          y=city3_df['price_2020_08'],
                          marker_color=styling.get('city3color'))
        figure_data.append(fig3_bar)

    # Instantiate figure.
    fig = go.Figure(data=figure_data)

    # Update general figure layout.
    if city3:
        fig.update_layout(barmode='group', title_text=styling.get('title'),
                        xaxis_title='Number of Bedrooms',
                        yaxis_title='Monthly Rental Estimate',
                        font=dict(size=10))
    else:
        # Update general figure layout.
        fig.update_layout(barmode='group', title_text=styling.get('title'),
                        xaxis_title='Number of Bedrooms',
                        yaxis_title='Monthly Rental Estimate')

    return fig.to_json()
