from fastapi import APIRouter
from app.sql_query_function import fetch_query_records
from dotenv import load_dotenv
import psycopg2
import os
import warnings
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px

router = APIRouter()

@router.get("/rental/predict/viz/{city}_{state}")
async def viz(city: str, state: str):

    def rental_predictions(city, state):
        warnings.filterwarnings("ignore", message="After 0.13 initialization must be handled at model creation")
        query = """
        SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
        FROM rental
        WHERE "city"='{city}' and "state"='{state}';
        """.format(city=city.title(), state=state.upper())

        df =  pd.DataFrame.from_records(fetch_query_records(query), columns=["month", "Studio", "onebr", "twobr", "threebr", "fourbr"])
        df.set_index("month", inplace=True)
        df.index = pd.to_datetime(df.index)
        df.index.freq = "MS"
        
        series = []

        for col in df.columns:
            s = ExponentialSmoothing(df["2014-06-01":][col].astype(np.int64), trend="add", seasonal="add", seasonal_periods=12).fit().forecast(12)
            s.name = col
            series.append(s)

        return pd.concat(series, axis=1).to_json(indent=2)

    df = pd.read_json(rental_predictions(city, state))
    df.columns = [
        "Studio",
        "One Bedroom",
        "Two Bedroom",
        "Three Bedroom",
        "Four Bedroom"
    ]
    fig = px.line(df, x=df.index, y=df.columns, title="Rental Price - Predicted",
    labels=dict(index="Month", value="Price in USD"),
    range_y=[0, df["Four Bedroom"].max()]
    )
    return fig.to_json()