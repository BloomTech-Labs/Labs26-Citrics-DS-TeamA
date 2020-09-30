from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from insert import retrieve
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import datetime
from psycopg2.extras import execute_values



register_adapter(np.int64, psycopg2._psycopg.AsIs)
register_adapter(np.float64, psycopg2._psycopg.AsIs)
register_adapter(np.datetime64, psycopg2._psycopg.AsIs)

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

def weather_pred(city: str, state: str, metric=None):
    df = retrieve(city=city, state=state)
    df.set_index("date_time", inplace=True)
    df.index = pd.to_datetime(df.index)

    data = df[metric]

    raw_series = {
        "min" : data.resample("MS").min(),
        "mean" : data.resample("MS").mean(),
        "median" : data.resample("MS").median(),
        "max" : data.resample("MS").max()
    }

    warnings.filterwarnings("ignore")

    series = []

    for d in raw_series.keys():
        s = ExponentialSmoothing(raw_series[d], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
        s.name = d
        series.append(s)

    result = pd.concat(series, axis=1)
    result.index = result.index.astype(str)
    result.insert(0, "city", [city] * len(result))
    result.insert(1, "state", [state] * len(result))

    for col in result.columns[2:]:
        result.loc[result[col] < 0.0, col] = 0.0

    create_table = """
    CREATE TABLE IF NOT EXISTS {metric}(
        month TIMESTAMP NOT NULL,
        city varchar(20) NOT NULL,
        state varchar(2) NOT NULL,
        min FLOAT NOT NULL,
        mean FLOAT NOT NULL,
        med FLOAT NOT NULL,
        max FLOAT NOT NULL
    );
    """.format(metric=metric)

    cur.execute(create_table)
    connection.commit()

    insert_data = """
    INSERT INTO {metric}(
        month,
        city,
        state,
        min,
        mean,
        med,
        max
    ) VALUES%s
    """.format(metric=metric)

    execute_values(cur, insert_data, list(result.to_records(index=True)))
    connection.commit()
    # return result.index


if __name__ == "__main__":
    weather_pred("Salt Lake City", "UT", "tempC")
    # print(weather_pred("Salt Lake City", "UT", "tempC"))
    # print(weather_pred("Salt Lake City", "UT", "tempC").index)