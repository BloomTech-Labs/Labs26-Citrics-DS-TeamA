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
import plotly.graph_objects as go

router = APIRouter()


@router.get("/rental/predict/{city}_{state}")
async def rental_price_predictions(city: str, state: str):
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

    as the average of the monthly prediction for `city` each year
    """
    # Edge Cases
    # Saint
    if city[0:5] == "Saint" or city[0:5] == "saint":
        city = city.replace(city[0:5], "St.")
    elif city[0:3] == "St " or city[0:3] == "st ":
        city = city.replace(city[0:3], "St.")
    # Fort
    elif city[0:3] == "Ft " or city[0:3] == "ft " :
        city = city.replace(city[0:3], "Fort ")
    elif city[0:3] == "Ft." or city[0:3] == "ft.":
        city = city.replace(city[0:3], "Fort")

    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()

    db.adapters(np.int64)

    if city[0:2] == "Mc":
        city = city[:2] + city[2:].capitalize()
        retrieve_records = """
        SELECT * FROM rental_pred
        WHERE "city"='{city}' and "state"='{state}'
        """.format(city=city, state=state.upper())

    else:
        retrieve_records = """
        SELECT * FROM rental_pred
        WHERE "city"='{city}' and "state"='{state}'
        """.format(city=city.title(), state=state.upper())

    cur.execute(retrieve_records)

    columns = [
        "year",
        "city",
        "state",
        "Studio",
        "onebr",
        "twobr",
        "threebr",
        "fourbr",
    ]

    result = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
    result.set_index("year", inplace=True)

    if len(result.index) == 0:
        warnings.filterwarnings(
            "ignore", message="After 0.13 initialization must be handled at model creation"
        )

        if city[0:2] == "Mc":
            query = """
            SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
            FROM rental
            WHERE "city"='{city}' and "state"='{state}';
            """.format(city=city, state=state.upper())

        else:
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

        def to_year(datetime_obj) -> int:
            return datetime_obj.year

        result = pd.concat(series, axis=1)
        result = result.resample("Y").mean()[1:3]
        result.reset_index(inplace=True)
        result["index"] = result["index"].apply(to_year)
        result.set_index("index", inplace=True)
        result.insert(0, "city", city)
        result.insert(1, "state", state)

        for col in result.columns[2:]:
            result[col] = result[col].astype(int)

        insert_data = """
        INSERT INTO rental_pred(
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
        conn.close()

    return result.to_json(indent=2)


# Unused visualization route...

# @router.get("/rental/predict/viz/{city}_{state}")
# async def viz(city: str, state: str):
#     """
#     **Input**

#     city: str  <- city name, any capitalization, spaces between multi-word city names are required

#     state: str <- two-letter state abbreviation, any capitalization

#     **Output**

#     json string for visualization showing rental price predictions:
#     - Studio
#     - One Bedroom
#     - Two Bedroom
#     - Three Bedroom
#     - Four Bedroom

#     for 24 months from the present (September 2020)

#     with "month" as the independent variable.
#     """
#     df = pd.read_json(await pred(city, state))[
#         ["Studio", "onebr", "twobr", "threebr", "fourbr"]]
#     df.columns = [
#         "Studio",
#         "One Bedroom",
#         "Two Bedroom",
#         "Three Bedroom",
#         "Four Bedroom"
#     ]
#     layout = go.Layout(
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         yaxis=dict(range=([500, df["Four Bedroom"].max() + 100]))
#     )

#     styling = {
#         "Studio": "lightgreen",
#         "One Bedroom": "#4BB543",
#         "Two Bedroom": "darkcyan",
#         "Three Bedroom": "#663399",
#         "Four Bedroom": "#CC0000"
#     }

#     fig = go.Figure(
#         data=go.Scatter(name=f"Rental Price - Predicted {city}, {state}"),
#         layout=layout
#     )

#     for col in df.columns:
#         fig.add_trace(go.Scatter(name=col, x=df.index,
#                                  y=df[col], mode='lines', marker_color=styling[col]))

#     fig.update_layout(
#         title=f"Rental Price - Predicted {city}, {state}",
#         yaxis_title="US Dollars",
#         font=dict(family='Open Sans, extra bold', size=10),
#         height=412,
#         width=640
#     )

#     return fig.to_json()
