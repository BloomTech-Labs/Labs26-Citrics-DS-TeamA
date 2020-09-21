import sys
from fastapi import APIRouter
import pandas as pd
import os
from app.smart_downer_function import smart_downer
from datetime import datetime
from app.splits import splits

router = APIRouter()

@router.get("/historic_weather/get_stats/{city}_{statecode}")
async def get_stats(city: str, statecode: str, stat: str, metric=True):
    """
    Extracts a Pandas DataFrame containing the
    - minimum,
    - mean,
    - median, and 
    - maximum

    for the desired weather metric (stat) for the desired city.

    stat takes one of the following metrics as a parameter:
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

    # Creating subsetted Series for each month in the data
    subsets = []

    # Checking length of DataFrame index,
    # determines whether the data is long or short

     # Subsetting short data
    if len(series.index) == 16440:
        for j in range(len(splits[3:-3]) - 1):
            subset = series[series.index > splits[j]]
            subset = series[series.index < splits[j + 1]]
            subsets.append(subset)

        subsets = subsets[2:]

    # Subsetting long data
    else:
        for j in range(len(splits[1:-2]) - 1):
            subset = series[series.index > splits[j]]
            subset = series[series.index < splits[j + 1]]

    # Calculating stats for series
    tables = []
    time = []

    for sub in subsets:
        tables.append(sub.describe()[1:])
        time.append(datetime(sub.index[0].year, sub.index[0].month, sub.index[0].day))

    # Populating new DataFrame with the above stats
    minimum = []
    mean = []
    med = []
    maximum = []

    for i in range(len(tables)):
        mean.append(tables[i]["mean"])
        minimum.append(tables[i]["min"])
        med.append(tables[i]["50%"])
        maximum.append(tables[i]["max"])

    data = {
        "month" : time,
        "mean" : mean,
        "min" : minimum,
        "med" : med,
        "max" : maximum
    }

    df = pd.DataFrame(data)

    # Resetting new DataFrame index to the datetime of the first entry
    df.set_index("month", inplace=True)
    
    # Setting freq of df's index to "MS" for monthly
    df.index.freq = "MS"

    return df