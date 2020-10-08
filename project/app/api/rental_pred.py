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

    def rental_predictions(city, state):

        db = PostgreSQL()
        conn = db.connection()
        cur = conn.cursor()

        db.adapters(np.float64)

        retrieve_records = """
        SELECT * FROM rental_pred
        WHERE "city"='{city}' and "state"='{state}'
        """.format(city=city.title(), state=state.upper())

        cur.execute(retrieve_records)

        columns = [
            "month",
            "city",
            "state",
            "Studio",
            "onebdr",
            "twobdr",
            "threebdr",
            "fourbdr"
        ]

        result = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
        result.set_index("month", inplace=True)
        result.index = pd.to_datetime(result.index)

        if len(result.index) == 0:
            warnings.filterwarnings(
                "ignore", message="After 0.13 initialization must be handled at model creation")
            query = """
            SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
            FROM rental
            WHERE "city"='{city}' and "state"='{state}';
            """.format(city=city.title(), state=state.upper())

            df = pd.DataFrame.from_records(fetch_query_records(query), columns=[
                                           "month", "Studio", "onebr", "twobr", "threebr", "fourbr"])
            df.set_index("month", inplace=True)
            df.index = pd.to_datetime(df.index)
            df.index.freq = "MS"

            series = []

            for col in df.columns:
                s = ExponentialSmoothing(df["2014-06-01":][col].astype(
                    np.int64), trend="add", seasonal="add", seasonal_periods=12).fit().forecast(12)
                s.name = col
                series.append(s)

            result = pd.concat(series, axis=1)
            result.index = result.index.astype(str)
            result.insert(0, "city", city)
            result.insert(1, "state", state)

            insert_data = """
            INSERT INTO rental_pred(
                month,
                city,
                state,
                Studio,
                onebdr,
                twobdr,
                threebdr,
                fourbdr
            ) VALUES%s
            """

            execute_values(cur, insert_data, list(
                result.to_records(index=True)))
            conn.commit()

        return result.to_json(indent=2)

    return rental_predictions(city, state)
