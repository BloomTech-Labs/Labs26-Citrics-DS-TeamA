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


@router.get("/census/predict/{city}_{state}")
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

    as the average of the monthly prediction for `city` each year
    """

    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()

    db.adapters(np.int64)

    retrieve_records = f"""
    SELECT
        city,
        state,
        popestimate2010,
        popestimate2011,
        popestimate2012,
        popestimate2013,
        popestimate2014,
        popestimate2015,
        popestimate2016,
        popestimate2017,
        popestimate2018,
        popestimate2019
    FROM census
    WHERE "city"='{city}' and "state"='{state}'
    """

    columns = [
        "city",
        "state",
        "popestimate2010",
        "popestimate2011",
        "popestimate2012",
        "popestimate2013",
        "popestimate2014",
        "popestimate2015",
        "popestimate2016",
        "popestimate2017",
        "popestimate2018",
        "popestimate2019"
    ]

    cur.execute(retrieve_records)

    df = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
    conn.close()
    return df.to_json(indent=2)