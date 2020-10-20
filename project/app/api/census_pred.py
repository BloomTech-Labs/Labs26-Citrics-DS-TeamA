# Note:
#  This route may have been a cause of a memory overload issue
#  which forced the Labs 26 DS team to need to redeploy the API,
#  so uncomment with caution.

# from fastapi import APIRouter
# from dotenv import load_dotenv
# import psycopg2
# import os
# from app.database import PostgreSQL
# import numpy as np
# import pandas as pd
# from datetime import datetime
# import warnings
# from statsmodels.tsa.holtwinters import ExponentialSmoothing
# from psycopg2.extras import execute_values
# from functools import reduce
# import plotly.graph_objects as go

# router = APIRouter()


# @router.get("/census/predict/{city}_{state}")
# async def predict_population(city: str, state: str):
#     """
#     *Input*

#     `city: str`  <- city name with any capitalization
    
#     `state: str` <- two-letter state abbreviation

#     *Output*

#     json object containing the predictions for two years from the
#     present (2020) for the population of the city, state inputted.
#     """

#     db = PostgreSQL()
#     conn = db.connection
#     cur = conn.cursor()

#     db.adapters(np.int64)

#     # Edge Cases
#     # Saint
#     if city[0:5] == "Saint" or city[0:5] == "saint":
#         city = city.replace(city[0:5], "St.")
#     elif city[0:2] == "St" or city[0:2] == "st":
#         city = city.replace(city[0:2], "St.")
#     # Fort
#     elif city[0:3] == "Ft " or city[0:3] == "ft ":
#         city = city.replace(city[0:3], "Fort ")
#     elif city[0:3] == "Ft." or city[0:3] == "ft.":
#         city = city.replace(city[0:3], "Fort")

#     if city[0:2] == "Mc":
#         query = f"""
#         SELECT *
#         FROM census_pred
#         WHERE "city"='{city}' and "state"='{state.upper()}'
#         """

#     else:       
#         query = f"""
#         SELECT *
#         FROM census_pred
#         WHERE "city"='{city.title()}' and "state"='{state.upper()}'
#         """

#     cur.execute(query)

#     df_preds = pd.DataFrame.from_records(
#         cur.fetchall(),
#         columns=["Year", "City", "State", "Population"]
#         )

#     df_preds.set_index("Year", inplace=True)

#     if len(df_preds.index) == 0:

#         columns = [
#             "city",
#             "state",
#             "popestimate2010",
#             "popestimate2011",
#             "popestimate2012",
#             "popestimate2013",
#             "popestimate2014",
#             "popestimate2015",
#             "popestimate2016",
#             "popestimate2017",
#             "popestimate2018",
#             "popestimate2019"
#         ]

#         if city[0:2] == "Mc":
#             retrieve_records = f"""
#                 SELECT
#                 """
#             for i in range(len(columns) - 1):
#                 retrieve_records += f"    {columns[i]},\n"

#             retrieve_records += f"    {columns[-1]}"
#             retrieve_records += f"""
#             FROM census
#             WHERE "city"='{city} city' and "state"='{state.upper()}'
#             """

#         else:
#             retrieve_records = f"""
#                 SELECT
#                 """
#             for i in range(len(columns) - 1):
#                 retrieve_records += f"    {columns[i]},\n"

#             retrieve_records += f"    {columns[-1]}"
#             retrieve_records += f"""
#             FROM census
#             WHERE "city"='{city.title()} city' and "state"='{state.upper()}'
#             """

#         cur.execute(retrieve_records)

#         series = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
#         series.city = [x.replace(" city","") for x in series.city.to_list()]
#         series = series.reset_index(drop=True).iloc[0].T
#         series.name = f"{series.city}, {series.state}"
#         series = series.take([n for n in range(4, len(series))])
#         series = series.rename(lambda x: datetime(int(x[-4:]), 12, 31))
#         # series.index.freq = "Y"

#         warnings.filterwarnings(
#             "ignore",
#             message="After 0.13 initialization must be handled at model creation"
#             )

#         preds = ExponentialSmoothing(
#             series.astype(np.int64),
#             trend="mul",
#             seasonal="mul",
#             seasonal_periods=2
#             ).fit().forecast(3)

#         preds.name = series.name
#         preds = preds.astype(int)
#         preds = preds.take([1, 2])
#         preds = preds.rename(lambda x: x.year)

#         insert_preds = """
#         INSERT INTO census_pred(
#             year,
#             city,
#             state,
#             population
#         )VALUES%s
#         """

#         s = [
#             pd.Series(
#                 data=[city] * len(preds.index),
#                 index=preds.index,
#                 name="city"
#                 ),
#             pd.Series(
#                 data=[state] * len(preds.index),
#                 index=preds.index,
#                 name="state"
#                 ),
#             preds
#         ]

#         df_preds = pd.concat(s, axis=1)

#         execute_values(
#             cur,
#             insert_preds,
#             list(df_preds.to_records(index=True))
#         )
        
#         conn.commit()

#     conn.close()
#     return df_preds.to_json(indent=2)