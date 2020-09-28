from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

register_adapter(np.int64, psycopg2._psycopg.AsIs)
register_adapter(np.float64, psycopg2._psycopg.AsIs)

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "Invalid DB_NAME value")
DB_USER = os.getenv("DB_USER", "Invalid DB_USER value")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Invalid DB_PASSWORD value")
DB_HOST = os.getenv("DB_HOST", "Invalid DB_HOST value")

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
    )

cur = connection.cursor()

def insert_csv(city=None, state=None, filepath=None):
    create_table = """
    CREATE TABLE IF NOT EXISTS historic_weather(
        date_time TIMESTAMP NOT NULL,
        location INT NOT NULL,
        city varchar(20) NOT NULL,
        state varchar(2) NOT NULL,
        tempC INT NOT NULL,
        FeelsLikeC INT NOT NULL,
        precipMM FLOAT NOT NULL,
        totalSnow_cm FLOAT NOT NULL,
        humidity INT NOT NULL,
        pressure INT NOT NULL
    );
    """

    cur.execute(create_table)
    connection.commit()

    if city and state:
        df = pd.read_csv(os.path.join("data", "weather", f"{city}_{state}.csv"))
        df = df[["date_time", "location", "tempC", "FeelsLikeC", "precipMM", "totalSnow_cm", "humidity", "pressure"]]
        df.insert(2, "city", [city.title()] * len(df.index))
        df.insert(3, "state", [state.upper()] * len(df.index))

    elif filepath:
        df = pd.read_csv(os.path.join("data", "weather", filepath))
        df = df[["date_time", "location", "tempC", "FeelsLikeC", "precipMM", "totalSnow_cm", "humidity", "pressure"]]
        df.insert(2, "city", [filepath[:-7].title()] * len(df.index))
        df.insert(3, "state", [filepath[-6:-4].upper()] * len(df.index))

    insert_data = """
    INSERT INTO historic_weather(
        date_time,
        location,
        city,
        state,
        tempC,
        FeelsLikeC,
        precipMM,
        totalSnow_cm,
        humidity,
        pressure
    ) VALUES%s
    """

    execute_values(cur, insert_data, list(df.to_records(index=False)))
    connection.commit()

def reset():
    reset_table = """
    DROP TABLE historic_weather;
    """
    cur.execute(reset_table)
    connection.commit()

def reset_city(city, state):
    delete = """
    DELETE FROM historic_weather
    WHERE "city"='{city}' and "state"='{state}'
    """.format(city=city.title(), state=state.upper())

    cur.execute(delete)
    connection.commit()

if __name__ == "__main__":
    input1 = input("""
    Welcome to the Historical Weather Database Insertion Utility!\n
    If you would like to insert a city, simply type 'insert' in the prompt
    below, then type the city name and state abbreviation when prompted.

    If you would like to repopulate the database with all the historic data
    found in the data/weather directory, type 'populate'

    If you would like to reset the entire Historic Weather Database, simply
    type 'reset'.

    If you would like to reset only those data for a single city, type
    'reset city', then type the desired city name and state abbreviation
    when prompted.
    """)

    if input1 == "reset":
        input2 = input("City: ")
        input3 = input("State: ")
        remove_city(input2, input3)

    elif input1 == "reset city":
        input2 = 

    elif input1 == "populate":
        csv_files = [f for f in os.listdir(os.path.join("data", "weather")) if f[-3:]  == "csv"]
        for f in csv_files:
            insert_csv(filepath=f)

    elif input1 == "exit" or input1 == "quit" or input1 == "q":
        sys.exit()

    else:
        input2 = input("City: ")
        input3 = input("State: ")
        insert_csv(input2, input3)