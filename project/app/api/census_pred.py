from fastapi import APIRouter
from dotenv import load_dotenv
import psycopg2
import os
from app.database import PostgreSQL
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from psycopg2.extras import execute_values
from functools import reduce
import plotly.graph_objects as go

router = APIRouter()


@router.get("/census/predict/{city}_{state}")
async def pred(city: str, state: str):
    """
    """

    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()

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

    series = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
    series = series.reset_index(drop=True).iloc[0].T
    series.name = f"{series.city}, {series.state}"
    series = series.take([n for n in range(4, len(series))])
    series = series.rename(lambda x: datetime(int(x[-4:]), 12, 31))

    warnings.filterwarnings(
        "ignore",
        message="After 0.13 initialization must be handled at model creation"
        )

    preds = ExponentialSmoothing(
        series.astype(np.int64),
        trend="mul",
        seasonal="mul",
        seasonal_periods=2
        ).fit().forecast(3)

    preds.name = series.name
    preds = preds.astype(int)
    preds = preds.take([1, 2])
    preds = preds.rename(lambda x: x.year)

    conn.close()
    return preds.to_json(indent=2)