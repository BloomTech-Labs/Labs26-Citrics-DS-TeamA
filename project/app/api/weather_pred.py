from fastapi import APIRouter
from typing import Optional
from psycopg2.extensions import register_adapter, AsIs
from dotenv import load_dotenv
import os
from app.database import PostgreSQL
import numpy as np
import psycopg2
import pandas as pd
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from psycopg2.extras import execute_values
import plotly.graph_objects as go
import io
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/weather/predict/{city}_{state}")
async def predict_temperatures(city: str, state: str, metric=False):
    """
    **Input**

    `city: str`    <- city name with any capitalization

    `state: str`   <- two-letter state abbreviation with any capitalization

    `metric: bool` <- *(Optional)* default, False, will output predictions and make
    database queries for adjusted temperature in degrees Fahrenheit;

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;
    True will do so for adjusted temperature in degrees Celsius.

    **Output**

    `json object` with predictions for
    
    **monthly temperature** of `city` and up to a total of three cities
    adjusted for dew point and wind chill for 24 months
    
    from the present (September 2020)
    """
    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()
    db.adapters(np.int64, np.float64, np.datetime64)

    # Edge Cases
    # Saint
    if city[0:3] == "St." or city[0:3] == "st.":
        city = city.replace(city[0:3], "St")
    elif city[0:5] == "Saint" or city[0:5] == "saint":
        city = city.replace(city[0:5], "St")
    # Fort
    elif city[0:3] == "Ft " or city[0:3] == "ft ":
        city = city.replace(city[0:3], "Fort ")
    elif city[0:3] == "Ft." or city[0:3] == "ft.":
        city = city.replace(city[0:3], "Fort")
    # multiple caps
    elif city[0:2] == 'Mc':
        city = city.replace(city, city[:2] + city[2:].capitalize())

    # If prediciton found in database
    # If metric values are desired:
    if metric == True:
        table = "feelslikec"

    else:
        table = "feelslikef"

    retrieve_pred = f"""
    SELECT month, mean
    FROM {table}
    WHERE "city"='{city.title()}' and "state"='{state.upper()}'
    """

    cur.execute(retrieve_pred)

    result = pd.DataFrame.from_records(
        cur.fetchall(),
        columns=["month", "mean"]
    )
    result.set_index("month", inplace=True)
    result.index = pd.to_datetime(result.index)

    result_json = result.to_json(index=2)

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
        Where "city"='{city.title()}' and "state"='{state.upper()}'
        """

        cur.execute(retrieve_data)

        df = pd.DataFrame.from_records(cur.fetchall())

        if len(df.index) == 0:
            result_json = f"{city}, {state} not found in Historic Weather Database."

        else:
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

            c = pd.Series([city.title()] * len(result.index))
            c.index = result.index
            s = pd.Series([state.upper()] * len(result.index))
            s.index = result.index

            result = pd.concat([c, s, result], axis=1)
            result.columns = ["city", "state", "temp"]
            result.index = result.index.astype(str)

            # Converting for temperature in Fahrenheit if needed
            # Conversion Helper Function
            def to_fahr(temp: float) -> float:
                return ((temp * 9) / 5) + 32

            if metric != True:
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
            result_json = result.to_json(indent=2)

        conn.close()
    return result_json


@router.get("/weather/predict/viz/{city1}_{state1}")
async def temperature_prediction_visualization(
    city1: str,
    state1: str,
    city2=None,
    state2=None,
    city3=None,
    state3=None,
    metric=None,
    view=None
):
    """
    **Input**

    `city1: str`   <- city name with any capitalization

    `state1: str`  <- two-letter state abbreviation with any capitalization

    `city2: str`   <- *(Optional)* city name with any capitalization

    `state2: str`  <- *(Optional)* two-letter state abbreviation with any capitalization

    `city2: str`   <- *(Optional)* city name with any capitalization

    `state2: str`  <- *(Optional)* two-letter state abbreviation with any capitalization

    `metric: bool` <- *(Optional)* default, False, will output visualization for predictions
    and make database queries for adjusted temperature in degrees Fahrenheit;

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;
    True will do so for adjusted temperature in degrees Celsius.

    `view` : str   <- *(Optional)* default None will render output as a json object,
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;
    "True" will return .png file of visualization

    **Output**

    `json object` *-see `view` under input-* of visualization of predictions for
    
    **monthly temperature** of `city1` and up to a total of three cities
    adjusted for dew point and wind chill for 24 months
    
    from the present (September 2020)
    """
    cities = []

    if (await predict_temperatures(city1.title(), state1.upper(), metric))[0] == "{":
        first = pd.read_json(await predict_temperatures(city1.title(), state1.upper(), metric))["mean"]
        first.name = f"{city1.title()}, {state1.upper()}"
        cities.append(first)

    if city2 and state2:
        if (await predict_temperatures(city2.title(), state2.upper(), metric))[0] == "{":
            second = pd.read_json(await predict_temperatures(city2.title(), state2.upper(), metric))["mean"]
            second.name = f"{city2.title()}, {state2.upper()}"
            cities.append(second)

    if city3 and state3:
        if (await predict_temperatures(city3.title(), state3.upper(), metric))[0] == "{":
            third = pd.read_json(await predict_temperatures(city3.title(), state3.upper(), metric))["mean"]
            third.name = f"{city3.title()}, {state3.upper()}"
            cities.append(third)

    if len(cities) > 0:
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        if metric == True:
            letter = "C"

        else:
            letter = "F"

        fig = go.Figure(
            data=go.Scatter(name=f"Adjusted Temperature {letter}"),
            layout=layout
        )

        for city in cities:
            fig.add_trace(go.Scatter(name=city.name, x=city.index, y=city.values))

        fig.update_layout(
            title=f"Adjusted Temperature {letter}",
            font=dict(family='Open Sans, extra bold', size=10),
            height=412,
            width=640
        )

        if view == "True":
            img = fig.to_image(format="png")
            return StreamingResponse(io.BytesIO(img), media_type="image/png")

        else:
            return fig.to_json()
    
    else:
        return "No Historic Weather Data found for any of the three cities."