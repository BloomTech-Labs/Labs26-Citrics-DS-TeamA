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
async def current(city: str, statecode: str, unit: Optional[str]=None):
    """Fetches current weather from:
    [OpenWeatherMap API](https://openweathermap.org/current),
    using any combination of city and state in the United States.

    ### Path Parameters
    `city`: City of which to retrieve current weather data.

    `statecode`:
    The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Query Parameter (Optional)
    `unit`:
    Choice in metric of weather (options: `imperial` for US standard, `metric` for the metric system). Defaults to imperial system.

    Usage: `current/city_statecode?unit=imperial`

    ### Response
    JSON output containtining the following:
    `city`, `visibility`, `clouds_all`, `main`, `description`,
    `main_temp`, `main_feels_like`, `main_temp_min`, `main_temp_max`, `main_pressure`,
    `main_humidity`, `wind_speed`, `wind_deg`.

    ### Metrics
    `main_temp`, `main_feels_like`, `main_temp_min`, `main_temp_max` are in Fahrenheit if imperial, or Celsius if metric.

    `visibility` is in miles if imperial, or meters if metric.

    `clouds_all` represents cloud cover, as a percentage.

    `wind_speed` is in miles per hour if imperial, or meters per second if metric.

    `pressure` is in Atmospheric pressure (hPa).

    """
    # Check if we have a unit. If not, we're gonna go ahead and use the imperial system as our metric.
    if unit is None:
        unit = 'imperial'
    else:
        # Make lowercase if the unit does exist.
        unit = unit.lower()

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
        if (feature == 'visibility') & (unit == 'imperial'):
            # mi = m * 0.00062137
            vis = response.get(feature) * 0.00062137
            fetched[feature] = round(vis, 1)
        # Otherise, if visibility / unit is metric, just store.
        elif (feature == 'visibility') & (unit == 'metric'):
            fetched[feature] = response.get(feature)

        # If the response is a list, filter and store data.
        if isinstance(response.get(feature), list):
            list_data = {k: v for k, v in response.get(feature)[0].items()
                         if k not in ['id', 'icon']}
            for k, v in list_data.items():
                fetched[k] = v

        # Check if the returned data is a dictionary. (temp, wind, clouds)
        if isinstance(response.get(feature), dict):
            for key, value in response.get(feature).items():
                # Check if key related to temperature for conversion.
                if key in ['temp', 'feels_like', 'temp_min', 'temp_max']:
                    if unit == 'imperial':
                        # Convert Kelvin to Fahrenheit.
                        # F = (((K - 273.15) * 9) / 5) + 32
                        f = round((((value - 273.15) * 9)/5) + 32, 1)
                        fetched[f'{feature}_{key}'] = str(f)
                    elif unit == 'metric':
                        # Convert Kelvin to Celsius if metric.
                        c = round(value - 273.15, 1)
                        fetched[f'{feature}_{key}'] = c
                elif key == 'speed':
                    if unit == 'imperial':
                        # Convert meters per second to miles per hour.
                        # mi = m * 0.00062137, 3600 seconds per hour.
                        speed = (value * 0.00062137) * 3600
                        # Round to 1 decimal space.
                        fetched[f'{feature}_{key}'] = round(speed, 1)
                    elif unit == 'metric':
                        # Simply append the value if metric.
                        fetched[f'{feature}_{key}'] = value
                else:
                    fetched[f'{feature}_{key}'] = value
    return json.dumps(fetched)
