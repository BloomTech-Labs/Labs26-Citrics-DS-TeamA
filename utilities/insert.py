from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
import sys

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

def deunderscore(string: str):
    list_ = list(string)
    for i in range(len(list_)):
        if list_[i] == "_":
            list_[i] = " "

    new_string = ""
    for char in list_:
        new_string += char
    
    return new_string

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
        df = pd.read_csv(os.path.join("data", "weather", "historic", f"{city}_{state}.csv"))
        df = df[["date_time", "location", "tempC", "FeelsLikeC", "precipMM", "totalSnow_cm", "humidity", "pressure"]]
        df.insert(2, "city", [deunderscore(city).title()] * len(df.index))
        df.insert(3, "state", [state.upper()] * len(df.index))

    elif filepath:
        df = pd.read_csv(os.path.join("data", "weather", "historic", filepath))
        df = df[["date_time", "location", "tempC", "FeelsLikeC", "precipMM", "totalSnow_cm", "humidity", "pressure"]]
        df.insert(2, "city", [deunderscore(filepath[:-7]).title()] * len(df.index))
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

def reset_city(city=None, state=None, location=None):
    delete = """
    DELETE FROM historic_weather
    WHERE "city"='{city}' and "state"='{state}'
    """.format(city=city.title(), state=state.upper())

    cur.execute(delete)
    connection.commit()

def retrieve(state=None, city=None, location=None):
    if state and city:
        retrieve_records = """
        SELECT * FROM historic_weather
        WHERE "city"='{city}' and "state"='{state}'
        """.format(city=city.title(), state=state.upper())

    elif location:
        retrieve_records = """
        SELECT * FROM historic_weather
        WHERE "location"='{location}'
        """.format(location=location)

    cur.execute(retrieve_records)

    columns = [
        "date_time",
        "location",
        "city",
        "state",
        "tempC",
        "FeelsLikeC",
        "precipMM",
        "totalSnow_cm",
        "humidity",
        "pressure"
    ]

    return pd.DataFrame.from_records(cur.fetchall(), columns=columns)

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

If you would like to retrieve data for a specific city, type 'retrieve'.
""")

    if input1 == "reset":
        reset()

    elif input1 == "reset city":
        input2 = input("City: ")
        input3 = input("State: ")
        reset_city(input2, input3)

    elif input1 == "populate":
        csv_files = [f for f in os.listdir(os.path.join("data", "weather", "historic")) if f[-3:]  == "csv"]
        for f in csv_files:
            insert_csv(filepath=f)

    elif input1 == "exit" or input1 == "quit" or input1 == "q":
        sys.exit()

    elif input1 == "insert":
        input2 = input("City: ")
        input3 = input("State: ")
        insert_csv(city=input2, state=input3)

    elif input1 == "retrieve":
        input2 = input("""
Would you like to retrieve the records by city name, or by zipcode?
For the former, type 'city';
for the latter, type 'location'.
""")
        if input2 == "city":
            input3 = input("City: ")
            input4 = input("State: ")
            print(retrieve(city=input3, state=input4))

        elif input2 == "location":
            input3 = input("Zip Code: ")
            print(retrieve(location=input3))

        else:
            print("""
Command not recognized.
'city' or 'location' are acceptable responses.
Check spelling, or
if you would like to leave the program without querying the
database, type 'exit', 'quit', or 'q'.
""")

    else:
        print("""
Command not recognized.
Check spelling, or
if you would like to leave the program without querying the
database, type 'exit', 'quit', or 'q'.
""")