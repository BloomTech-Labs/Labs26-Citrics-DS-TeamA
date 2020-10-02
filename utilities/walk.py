import os
import psycopg2
import pandas as pd
import requests
import time
from dotenv import load_dotenv
from sql_query_function import fetch_query

# Load environment variables from .env
load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
YELP_API = os.getenv("YELP_API")
WS_API_KEY = os.getenv("WS_API_KEY")

# SQL Query.
query = """
    SELECT
        city,
        "state",
        bedroom_size,
        price_2020_08
    FROM rp_clean1
    WHERE bedroom_size = 'Studio'
    """

# Columns to fetch
columns = ["city", "state", "bedroom_size", "price_2020_08"]

# Load json into pandas.
df = pd.read_json(fetch_query(query, columns))

# Empty arrays to populate with cities and states.
cities, states = [], []

# Append cities.
for city in df['city']:
    cities.append(city)
# Append states.
for state in df['state']:
    states.append(state)

# Create connection; create table if it doesn't already exist.
conn = psycopg2.connect(
                        dbname=DB_NAME,
                        user=DB_USER,
                        password=DB_PASSWORD,
                        host=DB_HOST)
curs = conn.cursor()
curs.execute('''CREATE TABLE IF NOT EXISTS WALKABILITY
             (city STR(100) PRIMARY KEY,
             walkscore FLOAT NOT NULL);''')
conn.commit()
curs.close()
conn.close()  # Close connection.

# Iterate through array, making requests for each city / state fetched.
for i in range(len(cities)):
    # Create connection / cursor.
    conn = psycopg2.connect(
                            dbname=DB_NAME,
                            user=DB_USER,
                            password=DB_PASSWORD,
                            host=DB_HOST)
    curs = conn.cursor()

    # Current city / state
    city = cities[i]
    state = states[i]
    citystate = f'{city}, {state}'

    # Headers, parameters (location and # of addresses to fetch (50 limit))
    headers = {'Authorization': 'Bearer {}'.format(YELP_API)}
    params = {'location': f'"{cities[i]}, {states[i]}"',
              'limit': 50}
    req = requests.get('https://api.yelp.com/v3/businesses/search',
                       headers=headers, params=params)
    # Empty array to populate with calculated Walkscores.
    cityscores = []

    # Iterate through businesses, making walkscore requests.
    for business in req.json()['businesses']:
        # Latitude / Longitude / Address needed for Walkscore API.
        lat = business['coordinates']['latitude']
        lon = business['coordinates']['longitude']
        address = business['location']['address1']
        # Query
        q = ("https://api.walkscore.com/score?format=json" +
             f"&address={address}&lat={lat}&lon={lon}" +
             f"&wsapikey={WS_API_KEY}")
        # Make request; store json.
        ws_req = requests.get(q).json()
        # Confirm Walkscore data has been returned and append if so.
        if ws_req.get('walkscore'):
            cityscores.append(ws_req.get('walkscore'))
        # Maximize API calls / sleep (5000 / day maximum for Walkscore API)
        time_sleep = 1 / ((5000 / 24 / 60 / 60))
        time.sleep(time_sleep)


    # Average walkscores.
    walk = round(sum(cityscores) / len(cityscores), 2)

    print(f'Inserting: {citystate} - Walkscore: {walk} ({i} / {len(cities)})')
    # Insert into database, commit changes, and close connection.
    curs.execute(f'''INSERT INTO WALKABILITY (city, walkscore)
                     VALUES ('{citystate}', {walk}) ON CONFLICT (city)
                     DO UPDATE SET walkscore={walk};''')
    conn.commit()
    conn.close()
