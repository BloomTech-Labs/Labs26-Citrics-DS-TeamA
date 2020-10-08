# preroutes_and_utilities/weather.pred <- preroute

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
import plotly.graph_objects as go

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


def weather_pred(city: str, state: str, metric: str):
    # If prediciton found in database:
    retrieve_records = """
    SELECT * FROM {metric}
    WHERE "city"='{city}' and "state"='{state}'
    """.format(metric=metric, city=city.title(), state=state.upper())

    cur.execute(retrieve_records)

    columns = [
        "month",
        "city",
        "state",
        "min",
        "mean",
        "max"
    ]

    result = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
    result.set_index("month", inplace=True)
    result.index = pd.to_datetime(result.index)

    # If prediction not found in database
    if len(result.index) == 0:
        df = retrieve(city=city, state=state)
        df.set_index("date_time", inplace=True)
        df.index = pd.to_datetime(df.index)

        data = df[metric]

        raw_series = {
            "min": data.resample("MS").min(),
            "mean": data.resample("MS").mean(),
            "max": data.resample("MS").max()
        }

        warnings.filterwarnings("ignore")

        series = []

        for d in raw_series.keys():
            s = ExponentialSmoothing(
                raw_series[d], trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
            s.name = d
            series.append(s)

        result = pd.concat(series, axis=1)
        print(result)
        result.index = result.index.astype(str)
        result.insert(0, "city", [city] * len(result))
        result.insert(1, "state", [state] * len(result))

        if metric != "tempC" and metric != "FeelsLikeC":
            for col in result.columns[2:]:
                result.loc[result[col] < 0.0, col] = 0.0

        insert_data = """
        INSERT INTO {metric}(
            month,
            city,
            state,
            min,
            mean,
            max
        ) VALUES%s
        """.format(metric=metric)

        execute_values(cur, insert_data, list(result.to_records(index=True)))
        connection.commit()

    return result.to_json()


def viz(city: str, state: str, metric: str):

    nomenclature = {
        "tempC" : ("Temperature", "Deg. C"),
        "FeelsLikeC" : ("Temperature Adjusted for Dew Point and Wind Chill", "Deg. C"),
        "precipMM" : ("Precipitation", "Milimeters"),
        "totalSnow_cm" : ("Snow", "Centimeters")
    }

    df = pd.read_json(weather_pred(city, state, metric))[["min", "mean", "max"]]
    df.columns = ["Low", "Average", "High"]
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig = go.Figure(
        data=go.Scatter(name=f"{nomenclature[metric][0]}"),
        layout=layout
    )

    for col in df.columns:
        fig.add_trace(go.Scatter(name=col, x=df.index, y=df[col], mode='lines'))

    return fig.show()


if __name__ == "__main__":
    viz("Salt Lake City", "UT", "tempC")