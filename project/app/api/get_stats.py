import sys
from fastapi import APIRouter
import pandas as pd
import os
from app.smart_downer_function import smart_downer
from datetime import datetime
from app.get_funcs import get_min, get_mean, get_med, get_max

router = APIRouter()

@router.get("/historic_weather/get_stats/{city}_{statecode}")
async def get_stats(city: str, statecode: str, metric: str, stat: str):
    """
    Extracts a json string containing the desired stat for the desired
    metric for each month found in the data.

    for the desired weather metric (stat) for the desired city.

    metric takes one of the following metrics as a parameter:
    - tempC
    - FeelsLikeC
    - humidity
    - pressure
    
    Not included yet in release 1, but release 2 will incoroporate
    a feature wherein if metric is set to false, the data will be
    returned in imperial units.

    Primarily for use by the DS team in building predictive models.
    Will be used under-the-hood in sending predictions and visualizations
    to the front end.
    """
    # Loading in csv as Pandas DataFrame
    city = smart_downer(city)
    DataFrame = pd.read_csv(os.path.join("data", "weather", f"{city}_{statecode}.csv"))

    # Fixing datetime format
    DataFrame.date_time = DataFrame.date_time.apply(lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))

    # Pulling Series for desired metric out of DataFrame
    series = DataFrame[stat]
    series.index = DataFrame.date_time

    if stat == "min":
        return get_min(series, rule="MS").to_json()
        
    elif stat == "mean":
        return get_mean(series, rule="MS").to_json()
        
    elif stat == "med":
        return get_med(series, rule="MS").to_json()
        
    elif stat == "max":
        return get_max(series, rule="MS").to_json()