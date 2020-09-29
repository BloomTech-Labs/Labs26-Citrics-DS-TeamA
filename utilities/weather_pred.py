from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from insert import retrieve
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

def weather_pred(city: str, state: str, statistic: str):
    df = retrieve(city=city, state=state)
    df.set_index("date_time", inplace=True)
    df.index = pd.to_datetime(df.index)

    if statistic == "min":
        df = df.resample("MS").min()

    elif statistic == "mean":
        df = df.resample("MS").mean()

    elif statistic == "median":
        df = df.resample("MS").median()

    elif statistic == "max":
        df = df.resample("MS").max()

    else:
        print("Exiting program...")
        sys.exit()

    warnings.filterwarnings("ignore")

    series = []

    for col in df.columns[3:]:
        s = ExponentialSmoothing(df[col], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
        s.name = col
        series.append(s)

    result = pd.concat(series, axis=1)
    result.insert(0, "city", [city] * len(result))
    result.insert(1, "state", [state] * len(result))

    for col in result.columns[2:]:
        result.loc[result[col] < 0.0, col] = 0.0

    return result


if __name__ == "__main__":
    stats = ["min", "mean", "median", "max"]
    print(weather_pred(city="Salt Lake City", state="UT", statistic="mean"))