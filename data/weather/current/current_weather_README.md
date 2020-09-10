# Using current_weather.py

The current_weather.py file is set up to use the [OpenWeatherMap API](https://openweathermap.org/api) to access current weather data. This script will pull the following information from the API, and write to a CSV file:
- zip
- name
- visibility
- timezone
- clouds_all
- weather_main
- weather_description
- main_temp
- main_feels_like
- main_temp_min
- main_temp_max
- main_pressure
- main_humidity
- wind_speed
- wind_deg
- wind_gust

## Instructions

### Open an Account for the API

Follow the instructions in [this link](https://home.openweathermap.org/users/sign_up) to create an account with the OpenWeatherMap API. You will receive an API key to be used.

### Packages

Before attempting to use the weather.py file, make sure to check that you have the correct versions of **python-dotenv**. **pandas**, and **numpy** as listed in the global requirements.txt file.

If not using a virtual environment or if using conda:
```
pip list
```

If using Pipenv

```
pipenv run pip list
```


### Running the current_weather.py file

The current_weather.py file is setup to take the zip codes in accordance to the lexicon .txt file.
Simply running the `current_weather.py` file will save the CSV file to `./data/weather/current/current_weather.csv`.