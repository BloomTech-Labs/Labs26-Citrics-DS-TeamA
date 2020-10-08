# preroutes_and_utitilites/rental_pred.py <- preroute

from database import PostgreSQL
from dotenv import load_dotenv
import psycopg2
import os
import warnings
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from psycopg2.extras import execute_values
import plotly.graph_objects as go
import io


def view(city: str, state: str):
    """
    **Input**

    city: str  <- city name, any capitalization, spaces between multi-word city names are required

    state: str <- two-letter state abbreviation, any capitalization

    **Output**

    json string for visualization showing rental price predictions:
    - Studio
    - One Bedroom
    - Two Bedroom
    - Three Bedroom
    - Four Bedroom

    for 24 months from the present (September 2020)

    with "month" as the independent variable.
    """

    def rental_predictions(city, state):

        db = PostgreSQL()
        conn = db.connection
        cur = conn.cursor()

        db.adapters(np.float64, np.datetime64)

        retrieve_records = """
        SELECT * FROM rental_pred
        WHERE "city"='{city}' and "state"='{state}'
        """.format(city=city.title(), state=state.upper())

        cur.execute(retrieve_records)

        columns = [
            "month",
            "city",
            "state",
            "Studio",
            "onebr",
            "twobr",
            "threebr",
            "fourbr",
        ]

        result = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
        result.set_index("month", inplace=True)

        if len(result.index) == 0:
            warnings.filterwarnings(
                "ignore", message="After 0.13 initialization must be handled at model creation")
            query = """
            SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
            FROM rental
            WHERE "city"='{city}' and "state"='{state}';
            """.format(city=city.title(), state=state.upper())

            cur.execute(query)

            df = pd.DataFrame.from_records(cur.fetchall(), columns=[
                                           "month", "Studio", "onebr", "twobr", "threebr", "fourbr"])
            df.set_index("month", inplace=True)
            df.index = pd.to_datetime(df.index)
            df.index.freq = "MS"

            series = []

            for col in df.columns:
                s = ExponentialSmoothing(df[col].astype(
                    np.int64), trend="add", seasonal="add", seasonal_periods=12).fit().forecast(24)
                s.name = col
                series.append(s)

            result = pd.concat(series, axis=1)
            result.index = result.index.astype(str)
            result.insert(0, "city", city)
            result.insert(1, "state", state)

            insert_data = """
            INSERT INTO rental_pred(
                month,
                city,
                state,
                Studio,
                onebdr,
                twobdr,
                threebdr,
                fourbdr
            ) VALUES%s
            """

            execute_values(cur, insert_data, list(
                result.to_records(index=True)))
            conn.commit()

        return result.to_json(indent=2)

    df = pd.read_json(rental_predictions(city, state))[
        ["Studio", "onebr", "twobr", "threebr", "fourbr"]]
    df.columns = [
        "Studio",
        "One Bedroom",
        "Two Bedroom",
        "Three Bedroom",
        "Four Bedroom"
    ]
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=([500, df["Four Bedroom"].max() + 100]))
    )

    styling = {
        "Studio": "lightgreen",
        "One Bedroom": "#4BB543",
        "Two Bedroom": "darkcyan",
        "Three Bedroom": "#663399",
        "Four Bedroom": "#CC0000"
    }

    fig = go.Figure(
        data=go.Scatter(name=f"Rental Price - Predicted {city}, {state}"),
        layout=layout
    )

    for col in df.columns:
        fig.add_trace(go.Scatter(name=col, x=df.index,
                                 y=df[col], mode='lines', marker_color=styling[col]))

    fig.update_layout(
        title=f"Rental Price - Predicted {city}, {state}",
        yaxis_title="US Dollars",
        font=dict(family='Open Sans, extra bold', size=10),
        height=412,
        width=640
    )
    return fig.show()


if __name__ == "__main__":
    view("New York", "NY")
