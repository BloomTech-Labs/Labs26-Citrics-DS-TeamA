from fastapi import APIRouter
import psycopg2
import os
import warnings
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

router = APIRouter()

@router.get("/rental/predict/{city}_{state}")
async def pred(city: str, state: str):

    DB_USER = "citrics"
    DB_PASSWORD = "BnDW2WupbFpgZSewsZm7"
    DB_NAME = "postgres"
    DB_HOST = "citricsads.cav8gkdxva9e.us-east-1.rds.amazonaws.com"

    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
        )

    cur = connection.cursor()

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

        return pd.concat(series, axis=1)

    return rental_predictions(city, state)