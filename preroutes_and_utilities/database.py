# preroutes_and_utilities/database.py <- utility

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

    def adapters(self, *args):
        for adapter in args:
            register_adapter(adapter, psycopg2._psycopg.AsIs)

    def close(self):
        self.connection.close()
