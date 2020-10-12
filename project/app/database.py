from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import pandas as pd

# Load environment variables from .env
load_dotenv()


class PostgreSQL:
    def __init__(self):
        self.name = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.connection = psycopg2.connect(
            dbname=self.name,
            user=self.user,
            password=self.password,
            host=self.host
        )

    def adapters(*args):
        for adapter in args:
            register_adapter(adapter, psycopg2._psycopg.AsIs)

    def cursor(self):
        self.cursor = self.connection.cursor()

    def execute(self, query):
        self.cursor.execute(query)

    def close(self):
        self.connection.close()

    def fetch_query_records(self, query: str):
        self.connection.cursor().execute(query)
        response = list(self.connection.cursor().catchall())
        self.connection.close()
        return response

    def fetch_query(self, query: str, columns: list):
        self.fetch_query_records(query)
        df = pd.DataFrame(response, columns=columns)
        return df.to_json(orient=records)
