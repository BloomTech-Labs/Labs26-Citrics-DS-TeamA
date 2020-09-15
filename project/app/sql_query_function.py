import os
import psycopg2
import pandas as pd 
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def fetch_query(query, columns):
    """
    Creates a connection to database, returns query from specified table
    as a list of dictionaries.

    Input: query: a SQL query (string)
    """
    # DB_NAME = os.getenv("DB_NAME")
    # DB_USER = os.getenv("DB_USER")
    # DB_PASSWORD = os.getenv("DB_PASSWORD")
    # DB_HOST = os.getenv("DB_HOST")

    DB_USER="citrics"
    DB_PASSWORD="BnDW2WupbFpgZSewsZm7"
    DB_NAME="postgres"
    DB_HOST="citricsads.cav8gkdxva9e.us-east-1.rds.amazonaws.com"

    # Creating Connection Object
    conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST)
    # Creating Cursor Object
    cursor = conn.cursor()
    # Fetch comments query
    query = query
    # Execute query
    cursor.execute(query)
    # Query results
    comments = list(cursor.fetchall())
    # Key-value pair names for df columns
    columns = columns
    # List of tuples to DF
    df = pd.DataFrame(comments, columns=columns)
    print(type(df))
    # DF to dictionary
    pairs = df.to_json(orient='records')
    print(type(pairs))
    # Closing Connection
    conn.close()

    return pairs