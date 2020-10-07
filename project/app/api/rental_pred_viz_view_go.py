from fastapi import APIRouter
from app.database import PostgreSQL
from app.sql_query_function import fetch_query_records
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
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/rental/predict/viz/viewgo/{city}_{state}")
async def view(city: str, state: str):
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
        conn = db.connection()
        cur = conn.cursor()

        db.adapters(np.float64)

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
        result.set_index("month")
        result.index = pd.to_datetime(result.index)

        if len(result.index) == 0:
            warnings.filterwarnings("ignore", message="After 0.13 initialization must be handled at model creation")
            query = """
            SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
            FROM rental
            WHERE "city"='{city}' and "state"='{state}';
            """.format(city=city.title(), state=state.upper())

            cur.execute(query)

            df =  pd.DataFrame.from_records(cur.fetchall(), columns=["month", "Studio", "onebr", "twobr", "threebr", "fourbr"])
            df.set_index("month", inplace=True)
            df.index = pd.to_datetime(df.index)
            df.index.freq = "MS"
            
            series = []

            for col in df.columns:
                s = ExponentialSmoothing(df["2014-06-01":][col].astype(np.int64), trend="add", seasonal="add", seasonal_periods=12).fit().forecast(12)
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

            execute_values(cur, insert_data, list(result.to_records(index=True)))
            conn.commit()

        return result.to_json(indent=2)
        
    df = pd.read_json(rental_predictions(city, state))[["Studio", "onebr", "twobr", "threebr", "fourbr"]]
    df.columns = [
        "Studio",
        "One Bedroom",
        "Two Bedroom",
        "Three Bedroom",
        "Four Bedroom"
    ]
    layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    # fig = px.line(df, x=df.index, y=df.columns, title="Rental Price - Predicted, {city}, {state}",
    # labels=dict(index="Month", value="Price in USD"),
    # range_y=[0, df["Four Bedroom"].max() + 100]
    # )
    fig = go.Figure(layout=layout)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Studio'], mode='lines'))


    fig.update_layout(
        font=dict(family='Open Sans, extra bold', size=10),
        height=412,
        width=640
        )

    img = fig.to_image(format="png")
    return StreamingResponse(io.BytesIO(img), media_type="image/png")
    