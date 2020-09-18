from fastapi import APIRouter
import pandas as pd
import os
from datetime import datetime

router = APIRouter()

@router.get("/historic_weather/get_stats/{city}_{statecode}")
async def get_stats(city, statecode, stat, metric=True):
    # Load in csv as Pandas DataFrame
    DataFrame = pd.read_csv(os.path.join("data", "weather", f"{city}_{statecode}.csv"))

    # Fix datetime format
    DataFrame.date_time = DataFrame.date_time.apply(lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))

    # Pull Series for desired metric out of DataFrame
    series = DataFrame[stat]
    series.index = DataFrame.date_time