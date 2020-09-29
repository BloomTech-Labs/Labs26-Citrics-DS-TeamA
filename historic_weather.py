from utilities.insert import retrieve
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing

register_adapter(np.int64, psycopg2._psycopg.AsIs)
register_adapter(np.float64, psycopg2._psycopg.AsIs)

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "Invalid DB_NAME value")
DB_USER = os.getenv("DB_USER", "Invalid DB_USER value")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Invalid DB_PASSWORD value")
DB_HOST = os.getenv("DB_HOST", "Invalid DB_HOST value")

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
    )

cur = connection.cursor()

def historic_pred(city=None, state=None, location=None):
    if city and state:
        df = retrieve(city=city, state=state)

    elif location:
        df = retrieve(location=location)

    df.set_index("date_time", inplace=True)
    df.index = pd.to_datetime(df.index)

    minimum = df.resample("MS").min()
    mean = df.resample("MS").mean()
    maximum = df.resample("MS").max()

    warnings.filterwarnings("ignore")

    series = []

    for col in minimum.columns[3:]:
        s = ExponentialSmoothing(df[col], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
        s.name = col + " min"
        series.append(s)

    for col in mean.columns[3:]:
        s = ExponentialSmoothing(df[col], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
        s.name = col + " mean"
        series.append(s)

    for col in maximum.columns[3:]:
        s = ExponentialSmoothing(df[col], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
        s.name = col + " max"
        series.append(s)

    return pd.concat(series, axis=1).to_json(indent=2)

if __name__ == "__main__":
    print(historic_pred(city="Salt Lake City", state="UT"))