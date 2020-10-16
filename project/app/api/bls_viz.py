import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.sql_query_function import fetch_query

import pandas as pd
import plotly.graph_objects as go

router = APIRouter()


@router.get('/bls_viz/{city}_{statecode}')
async def bls_viz(city: str, statecode: str, view=False):
    """
    Most prevelant job industry (city-level) per "Location Quotient" from
    [Burea of Labor Statistics](https://www.bls.gov/oes/tables.htm) 📈

    ## Path Parameters
    `city`: The name of a U.S. city; e.g. `Atlanta` or `Los Angeles`

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    `view`: If 'True' (string), returns a PNG instead of JSON

    ## Response
    Visualization of most prevelant job industries for more than 350
    U.S. cities.
    """

    # Query for all jobs that have associated annual wage data
    query = """
    SELECT *
    FROM bls_jobs
    WHERE annual_wage > 0
    """

    columns = ["city", "state", "occ_title", "jobs_1000", "loc_quotient", 
            "hourly_wage", "annual_wage"]

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

    # multiple caps
    elif city[0:2] == 'Mc':
        city = city[:2] + city[2:].capitalize()

    # Find matching metro-area in database
    match = df.loc[(df.city.str.contains(city)) &
                   (df.state.str.contains(statecode))]

    # Raise HTTPException for unknown inputs
    if len(match) < 1:
        raise HTTPException(
            status_code=404,
            detail=f'{city}, {statecode} not found!')

    # Subset of top jobs for matching city
    sub = match.sort_values(['city','loc_quotient'],ascending=False).groupby('city').head(10)
    sub = sub.reset_index()
    sub = sub.drop("index",axis=1)

    ### Begin Visualization
    styling = dict()

    styling['city1color'] = '#CC0000'  # red

    # Set background to be transparent.
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Set Title
    styling["title"] = "Hover over bars for Job Industry"

    x = sub["occ_title"]
    y= sub["annual_wage"]

    color_scale = "tealgrn"

    fig = go.Figure(data=go.Bar(name=f'{city}, {statecode}',
                                x=x,
                                y=y,
                                marker=dict(color=y, colorscale=color_scale)),
                                layout=layout)

    fig.update_layout(barmode='group', title_text=styling.get('title'),
                    xaxis_title='10 Most Prevelant Jobs (left to right, descending)',
                    yaxis_title='Average Annual Salary',
                    font=dict(family='Open Sans, extra bold', size=10),
                    height=412,
                    width=640)

    fig.update_xaxes(showticklabels=True) # hide all the xticks

    if view and view.title() == "True":
        img = fig.to_image(format="png")
        return StreamingResponse(io.BytesIO(img), media_type="image/png")

    return fig.to_json()

    