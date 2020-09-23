from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv
import warnings
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

router = APIRouter()

@router.get("/rental/predict/{city}_{state}")
def rental_predictions(city, state):
    warnings.filterwarnings("ignore", message="After 0.13 initialization must be handled at model creation")
    query = """
    SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
    FROM rental
    WHERE "city"='{city}' and "state"='{state}';
    """.format(city=city, state=state)

    cur.execute(query)

    df =  pd.DataFrame.from_records(cur.fetchall(), columns=["month", "Studio", "onebr", "twobr", "threebr", "fourbr"])
    df.set_index("month", inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index.freq = "MS"
    
    series = []

    for col in df.columns:
        s = ExponentialSmoothing(df["2014-06-01":]["Studio"], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(12)
        s.name = col
        series.append(s)

    return pd.concat(series, axis=1).to_json(indent=2)