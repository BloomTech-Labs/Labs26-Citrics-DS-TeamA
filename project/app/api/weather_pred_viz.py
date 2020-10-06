from fastapi import APIRouter
from dotenv import load_dotenv
from app.database import PostgreSQL
import numpy as np
import psycopg2
import os
import warnings
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px

router = APIRouter()

@router.get("/weather/predict/viz/{city}_{state}_{metric}")
async def viz(city: str, state: str, metric: str):

    def pred(city: str, state: str, metric: str):
        db = PostgreSQL()
        db.adapters(np.int64, np.float64, np.datetime64)
        connection = db.connection()
        cur = connection.cursor()

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
            "med",
            "max"
        ]

        result = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
        result.set_index("month", inplace=True)
        result.index = pd.to_datetime(result.index)

        # For use in historic weather retrieval.
        def retrieve(state: str, city: str):
            retrieve_records = """
            SELECT * FROM historic_weather
            WHERE "city"='{city}' and "state"='{state}'
            """.format(city=city.title(), state=state.upper())

            cur.execute(retrieve_records)

            columns = [
                "date_time",
                "location",
                "city",
                "state",
                "tempC",
                "FeelsLikeC",
                "precipMM",
                "totalSnow_cm",
                "humidity",
                "pressure"
            ]

            return pd.DataFrame.from_records(cur.fetchall(), columns=columns)

        # If prediction not found in database
        if len(result.index) == 0:
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

        return result.to_json()

    df = pd.read_json(pred(city, state, metric))[["min", "mean", "med", "max"]]
    fig = px.line(df, x=df.index, y=df.columns, title="{metric}- Predicted, {city}, {state}",
    labels=dict(index="Month", value=""),
    range_y=[0, df["max"].max() + 15]
    )

    fig.update_layout(
        font=dict(family='Open Sans, extra bold', size=10),
        height=412,
        width=640
        )
    return fig.to_json()