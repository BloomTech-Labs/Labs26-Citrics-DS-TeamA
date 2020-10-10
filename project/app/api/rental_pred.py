from fastapi import APIRouter
from app.database import PostgreSQL
from app.sql_query_function import fetch_query_records
from dotenv import load_dotenv
import psycopg2
import os
import warnings
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from psycopg2.extras import execute_values
from datetime import datetime
from functools import reduce
import plotly.graph_objects as go

router = APIRouter()


@router.get("/rental/predict/{city}_{state}")
async def pred(city: str, state: str):
    """
    **Input**

    city: str  <- city name, any capitalization, spaces between multi-word city names are required

    state: str <- two-letter state abbreviation, any capitalization

    **Output**

    json string containing rental price predictions:
    - Studio
    - One Bedroom
    - Two Bedroom
    - Three Bedroom
    - Four Bedroom

    for 24 months from the present (September 2020)

    with "month" attribute in json's datetime format.
    """

    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()

    db.adapters(np.float64, np.datetime64)

    retrieve_records = """
    SELECT * FROM rp
    WHERE "city"='{city}' and "state"='{state}'
    """.format(city=city.title(), state=state.upper())

    cur.execute(retrieve_records)

    columns = [
        "year",
        "city",
        "state",
        "Studio",
        "oner",
        "twor",
        "threebr",
        "fourbr",
    ]

    result = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
    result.set_index("year", inplace=True)

    if len(result.index) > 0:
        result = result.resample("Y").mean()[:2]

    if len(result.index) == 0:
        warnings.filterwarnings(
            "ignore", message="After 0.13 initialization must be handled at model creation"
        )
        query = """
        SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
        FROM rental
        WHERE "city"='{city}' and "state"='{state}';
        """.format(city=city.title(), state=state.upper())

        cur.execute(query)

        df = pd.DataFrame.from_records(
            cur.fetchall(),
            columns=["month", "Studio", "onebr", "twobr", "threebr", "fourbr"]
        )
        df.set_index("month", inplace=True)
        df.index = pd.to_datetime(df.index)
        df.index.freq = "MS"

        series = []

        for col in df.columns:
            s = ExponentialSmoothing(
                df[col].astype(np.int64),
                trend="add",
                seasonal="add",
                seasonal_periods=12
            ).fit().forecast(30)
            s.name = col
            series.append(s)

        result = pd.concat(series, axis=1)
        result = result.resample("Y").mean()[:2]
        result.index = result.index.astype(str)
        result.insert(0, "city", city)
        result.insert(1, "state", state)

        insert_data = """
        INSERT INTO rp(
            year,
            city,
            state,
            Studio,
            onebr,
            twobr,
            threebr,
            fourbr
        ) VALUES%s
        """

        execute_values(
            cur,
            insert_data,
            list(result.to_records(index=True))
        )
        conn.commit()

    return result.to_json(indent=2)


@router.get("/rental/predict/table/{city1}_{state1}")
async def table(
    city1: str,
    state1: str,
    city2=None,
    state2=None,
    city3=None,
    state3=None,
    metric=None
):
    columns = [
        "Year",
        "City",
        "State",
        "Studio",
        "One Bedroom",
        "Two Bedroom",
        "Three Bedroom",
        "Four Bedroom"
    ]

    dfs = []
    df1 = pd.read_json(await pred(city1, state1))
    df1.insert(0, "city", city1)
    df1.insert(1, "state", state1)
    df1 = df1.reset_index()
    df1.columns = columns
    dfs.append(df1)

    print(dfs[0].dtypes)

    if city2 and state2:
        df2 = pd.read_json(await pred(city2, state2))
        df2.insert(0, "city", city2)
        df2.insert(1, "state", state2)
        df2 = df2.reset_index()
        df2.columns = columns
        dfs.append(df2)

    if city3 and state3:
        df3 = pd.read_json(await pred(city3, state3))
        df3.insert(0, "city", city3)
        df3.insert(1, "state", state3)
        df3 = df3.reset_index()
        df3.columns = columns
        dfs.append(df3)

    def to_year(datetime_obj) -> int:
        return datetime_obj.year

    for DataFrame in dfs:
        DataFrame["Year"] = DataFrame["Year"].apply(to_year)
        for col in dfs[0].columns[3:]:
            DataFrame[col] = DataFrame[col].astype(int)

    if len(dfs) > 1:
        df = reduce(lambda left, right: pd.merge(
            left, right, how='outer', on=columns
            ), 
            dfs
        )

        print(df)

        return df.to_html(index=False)

    return dfs[0].to_html(index=False)

@router.get("/rental/predict/viz/{city}_{state}")
async def viz(city: str, state: str):
    """
    **Input**

    city: str  <- city name, any capitalization, spaces between multi-word city names are required

    state: str <- two-letter state abbreviation, any capitalization

    **Output**

    json string for visualization showing rental price predictions:
    - Studio
    - One Bedroom
    - Two Bedroom
    - Three Bedroom
    - Four Bedroom

    for 24 months from the present (September 2020)

    with "month" as the independent variable.
    """
    df = pd.read_json(await pred(city, state))[
        ["Studio", "onebr", "twobr", "threebr", "fourbr"]]
    df.columns = [
        "Studio",
        "One Bedroom",
        "Two Bedroom",
        "Three Bedroom",
        "Four Bedroom"
    ]
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=([500, df["Four Bedroom"].max() + 100]))
    )

    styling = {
        "Studio": "lightgreen",
        "One Bedroom": "#4BB543",
        "Two Bedroom": "darkcyan",
        "Three Bedroom": "#663399",
        "Four Bedroom": "#CC0000"
    }

    fig = go.Figure(
        data=go.Scatter(name=f"Rental Price - Predicted {city}, {state}"),
        layout=layout
    )

    for col in df.columns:
        fig.add_trace(go.Scatter(name=col, x=df.index,
                                 y=df[col], mode='lines', marker_color=styling[col]))

    fig.update_layout(
        title=f"Rental Price - Predicted {city}, {state}",
        yaxis_title="US Dollars",
        font=dict(family='Open Sans, extra bold', size=10),
        height=412,
        width=640
    )

    return fig.to_json()
