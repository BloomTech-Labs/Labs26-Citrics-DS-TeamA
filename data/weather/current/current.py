import ast
import csv
from dotenv import load_dotenv
import inspect
import numpy as np
import json
import os
import re
import requests
import sys

# Load API key.
load_dotenv()
API_KEY = os.environ.get('OPEN_WEATHER_KEY')

def fetch_current_weather(city1=None, city2=None, city3=None):
    # Fetch ZIP codes from locals.
    zip_codes = [value for value in locals().values() if isinstance(value, int)]

    # Features to fetch.
    features = ['name', 'visibility', 'clouds', 'weather', 'main', 'wind']
    
    fetched = []  # Empty array to populate with fetched data.
    response_data = []

    # Make query for each city.

            for item in features:
                # Check if response is a list, format if so.
                if isinstance(response.get(item), list):
                    # Let's update this with our appropriate values to use.
                    resp_data = {k: v for k, v in response.get(item)[0].items()
                                if k not in ['id', 'icon']}

                    # For the key and value in resp_data, check status of key in
                    # our features, then append it.
                    for k, v in resp_data.items():
                        if f'{item}_{k}' not in features:
                            features.append(f'{item}_{k}')
                        response_data.append(v)

                # If the item isn't a dictionary, append.
                elif not isinstance(response.get(item), dict):
                    response_data.append(response.get(item))

                # If the item is dict, re-format and append.
                elif isinstance(response.get(item), dict):
                    for key, value in response.get(item).items():
                        if f'{item}_{key}' not in features:
                            features.append(f'{item}_{key}')
                        if not isinstance(value, dict):
                            response_data.append(value)
    
    fetched.append(response_data)

    # Confirm there's existing items in each entry, as well as datatype.
    fetched = [x for x in fetched if not isinstance(x, list) and x]
    print(fetched)