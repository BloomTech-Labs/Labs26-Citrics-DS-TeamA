# preroutes_and_utilities/weather.pred <- preroute

from psycopg2.extensions import register_adapter, AsIs
from dotenv import load_dotenv
import os
from database import PostgreSQL
import numpy as np
import psycopg2
import pandas as pd
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import datetime
from psycopg2.extras import execute_values
import plotly.graph_objects as go

def weather_pred(city: str, state: str, si: bool):
    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()
    db.adapters(np.int64, np.float64, np.datetime64)

    # If prediciton found in database
    # If metric values are desired:
    if si == True:
        table = "feelslikec"

    else:
        table = "feelslikef"

    retrieve_pred = f"""
    SELECT month, mean
    FROM {table}
    WHERE "city"='{city}' and "state"='{state}'
    """

    cur.execute(retrieve_pred)

    result = pd.DataFrame.from_records(cur.fetchall(), columns=["month", "mean"])
    result.set_index("month", inplace=True)
    result.index = pd.to_datetime(result.index)

    if len(result.index) > 0:
        c = pd.Series([city] * len(result.index))
        c.index = result.index
        s = pd.Series([state] * len(result.index))
        s.index = result.index

        result = pd.concat([c, s, result], axis=1)
        result.columns = ["city", "state", "temp"]

    # If prediction not found in database
    elif len(result.index) == 0:
        retrieve_data = f"""
        SELECT date_time, FeelsLikeC
        FROM historic_weather
        Where "city"='{city}' and "state"='{state}'
        """

        cur.execute(retrieve_data)

        df = pd.DataFrame.from_records(cur.fetchall())
        df.set_index(0, inplace=True)
        series = df.resample("MS").mean()

        warnings.filterwarnings(
            "ignore",
            message="After 0.13 initialization must be handled at model creation"
            )

        result = ExponentialSmoothing(
            series.astype(np.int64),
            trend="add",
            seasonal="add",
            seasonal_periods=12
            ).fit().forecast(24)

        c = pd.Series([city] * len(result.index))
        c.index = result.index
        s = pd.Series([state] * len(result.index))
        s.index = result.index

        result = pd.concat([c, s, result], axis=1)
        result.columns = ["city", "state", "temp"]
        result.index = result.index.astype(str)

        # Converting for temperature in Fahrenheit if needed
        # Conversion Helper Function

        def to_fahr(temp: float) -> float:
            return ((temp * 9) / 5) + 32

        if si == False:
            result["temp"] = result["temp"].apply(to_fahr)

        insert_pred = """
        INSERT INTO {table}(
            month,
            city,
            state,
            mean
        ) VALUES%s
        """.format(table=table)

        execute_values(
            cur, 
            insert_pred,
            list(result.to_records(index=True))
            )
        conn.commit()

    return result.to_json(indent=2)


if __name__ == "__main__":
    print(weather_pred("Salt Lake City", "UT", True))
    print("")
    print(weather_pred("Salt Lake City", "UT", False))
