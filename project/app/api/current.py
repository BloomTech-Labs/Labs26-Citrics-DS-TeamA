from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from typing import Optional
import os
import json
import requests

router = APIRouter()

# Load API keys.
load_dotenv()

OW_API_KEY = os.environ.get('OW_API_KEY')


@router.get("/current/{city}_{statecode}")
async def current(city: str, statecode: str):
    """Fetches current weather from:
    [OpenWeatherMap API](https://openweathermap.org/current),
    using any combination of city and state in the United States.

    ### Path Parameters
    `city`: City of which to retrieve current weather data.

    `statecode`:
    The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Response
    JSON output containtining the following:
    `city`, `visibility`, `clouds_all`, `main`, `description`,
    `imperial_main_temp`, `imperial_main_feels_like`, `imperial_main_temp_min`, `imperial_main_temp_max`, 
    `metric_main_temp`, `metric_main_feels_like`, `metric_main_temp_min`, `metric_main_temp_max`,
    `main_pressure`,`main_humidity`, `imperial_wind_speed`, `metric_wind_speed`, `wind_deg`.

    ### Metrics
    `main_temp`, `main_feels_like`, `main_temp_min`, `main_temp_max` are in Fahrenheit if imperial, or Celsius if metric.

    `visibility` is in miles if imperial, or meters if metric.

    `clouds_all` represents cloud cover, as a percentage.

    `wind_speed` is in miles per hour if imperial, or meters per second if metric.

    `pressure` is in Atmospheric pressure (hPa).

    """

    statecode = statecode.upper()  # Ensure state code is uppercase.
    city = city.title()  # Capitalize first letter of city.

    query = ('https://api.openweathermap.org/data/2.5/' +
             f'weather?q={city},{statecode},US&appid={OW_API_KEY}')
    response = requests.get(query).json()
    fetched = {'city': f'{city}, {statecode}'}

    # Features we're going to be fetching from OWM JSON output.
    features = ['visibility', 'clouds', 'weather', 'main', 'wind']

    for feature in features:
        # If visibility and unit is imperial, make conversion.
        if feature == 'visibility':
            # mi = m * 0.00062137
            vis = response.get(feature) * 0.00062137
            fetched[f'imperial_{feature}'] = round(vis, 1)
            # Metric
            fetched[f'metric_{feature}'] = response.get(feature)

        # If the response is a list, filter and store data.
        if isinstance(response.get(feature), list):
            list_data = {k: v for k, v in response.get(feature)[0].items()
                         if k not in ['id', 'icon']}
            for k, v in list_data.items():
                # Capitalize first letter of each word in forecast.
                if k == 'description' or k == 'main':
                    v = v.title()
                fetched[k] = v

        # Check if the returned data is a dictionary. (temp, wind, clouds)
        if isinstance(response.get(feature), dict):
            for key, value in response.get(feature).items():
                # Check if key related to temperature for conversion.
                if key in ['temp', 'feels_like', 'temp_min', 'temp_max']:
                        # Convert Kelvin to Fahrenheit.
                        # F = (((K - 273.15) * 9) / 5) + 32
                        f = round((((value - 273.15) * 9)/5) + 32, 1)
                        fetched[f'imperial_{feature}_{key}'] = str(f)
                        # Convert Kelvin to Celsius.
                        # C = K - 273.15
                        c = round(value - 273.15, 1)
                        fetched[f'metric_{feature}_{key}'] = c

                elif key == 'speed':
                    # Convert meters per second to miles per hour.
                    # mi = m * 0.00062137, 3600 seconds per hour.
                    speed = (value * 0.00062137) * 3600
                    # Round to 1 decimal space.
                    fetched[f'imperial_{feature}_{key}'] = round(speed, 1)

                    # Metric
                    fetched[f'metric_{feature}_{key}'] = value
                else:
                    fetched[f'{feature}_{key}'] = value
    return json.dumps(fetched)
