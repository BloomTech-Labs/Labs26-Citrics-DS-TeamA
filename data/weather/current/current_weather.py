import ast
import csv
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import json
import os
import re
import requests

load_dotenv()
API_KEY = os.environ.get('API_KEY')

# Open file containing zip codes.
f = open('../lexicon.txt', 'r')

# Empty array of zip codes to populate.
zipcodes = []


# Check if there's a digit in line (ZIP code).
# If there is, add to array of zip codes.
for line in f:
    if re.findall(r'\d+', line):  # Check if numerical value exists.
        # If so, append it.
        zipcodes.append(re.findall(r'\d+', line))

# Data we're going to be fetching from API.
data_fetched = ['zip', 'name', 'visibility', 'timezone',
                'clouds', 'weather', 'main', 'wind']
fetched = []  # Array to populate with fetched data.

# For each zip code in lexicon.txt, we're gonna be making an API query.
for zip in zipcodes:
    # Make query.
    query = ("https://api.openweathermap.org/data/2.5/weather?" +
             f"zip={zip[0]},us&appid={API_KEY}")

    response = requests.get(query).json()
    fetched_items = []

    # Append each row to write.
    for item in data_fetched:

        # Our weather is stored in a list. Let's fix that.
        if isinstance(response.get(item), list):
            # Let's update this with our appropriate values to use.
            resp_data = {k: v for k, v in response.get(item)[0].items()
                         if k not in ['id', 'icon']}
            for k, v in resp_data.items():
                if f'{item}_{k}' not in data_fetched:
                    data_fetched.append(f'{item}_{k}')
                fetched_items.append(v)

        # Check if item is 'zip' - if so, append respective zip.
        if item == 'zip':
            fetched_items.append(zip[0])
        # If the item isn't 'zip', let's append the respective data.
        elif item != 'zip' and not isinstance(response.get(item), dict):
            fetched_items.append(response.get(item))

        # If the item is dict, re-format and append.
        elif isinstance(response.get(item), dict):
            for key, value in response.get(item).items():
                if f'{item}_{key}' not in data_fetched:
                    data_fetched.append(f'{item}_{key}')
                if not isinstance(value, dict):
                    fetched_items.append(value)

    # Confirm there's existing items in each entry, as well as datatype.
    fetched_items = [x for x in fetched_items if not isinstance(x, list) and x]
    fetched.append(fetched_items)  # Append for usage with pandas.


# Re-structure column names.
data_fetched = [x for x in data_fetched if
                x not in ['clouds', 'weather', 'main', 'wind']]

# Make into a pandas dataframe for easy export.
dataset = pd.DataFrame(data=[x for x in fetched],
                       columns=data_fetched)
dataset.to_csv('current_weather.csv', index=False, na_rep=np.NaN)
