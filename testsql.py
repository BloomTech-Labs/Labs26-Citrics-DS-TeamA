import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "Invalid DB_NAME value")
DB_USER = os.getenv("DB_USER", "Invalid DB_USER value")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Invalid DB_PW value")
DB_HOST = os.getenv("DB_HOST", "Invalid DB_HOST value")

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
    )

cur = connection.cursor()

query = """
SELECT "month", "Studio", "onebr", "twobr", "threebr", "fourbr"
FROM rental
WHERE "city"='King of Prussia' and "state"='PA';
"""

cur.execute(query)
records = cur.fetchall()

for row in records:
    print(row)
