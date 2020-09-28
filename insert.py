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

def insert_csv(city: str, state: str):
    create_table = """
    CREATE TABLE IF NOT EXISTS historic_weather(
        ID SERIAL PRIMARY KEY,
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

    df = pd.read_csv(os.path.join("data", "weather", f"{city}_{state}.csv"))
    df = df[["date_time", "location", "tempC", "FeelsLikeC", "precipMM", "totalSnow_cm", "humidity", "pressure"]]
    df.insert(2, "city", [city.title()] * len(df.index))
    df.insert(3, "state", [state.upper()] * len(df.index))

    insert_data = """
    INSERT INTO historic_weather(
        ID, 
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

    execute_values(cur, insert_data, list(df.to_records(index=True)))
    connection.commit()

if __name__ == "__main__":
    insert_csv("albuquerque", "nm")