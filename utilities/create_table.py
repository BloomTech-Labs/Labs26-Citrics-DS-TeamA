# utilities/create_table.py

from database import PostgreSQL
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import numpy as np

def create_table(table_name: str, columns: dict):

    db = PostgreSQL()
    conn = db.connection()
    cur = conn.cursor()

    db.adapters(np.float64)

    create_table = """
CREATE TABLE IF NOT EXISTS {table_name}(
""".format(table_name=table_name)

    for key in columns.keys():
        create_table += f"  {key} " + f"{columns[key]},\n"

    create_table = create_table[:-2]
    create_table += "\n);"

    cur.execute(create_table)
    conn.commit()

if __name__ == "__main__":
    table_name = "rental_pred"
    columns = {
        "month" : "TIMESTAMP NOT NULL",
        "city" : "varchar(20) NOT NULL",
        "state" : "varchar(2) NOT NULL",
        "Studio" : "FLOAT NOT NULL",
        "onebdr" : "FLOAT NOT NULL",
        "twobdr" : "FLOAT NOT NULL",
        "threebdr" : "FLOAT NOT NULL",
        "fourbdr" : "FLOAT NOT NULL"
    }

    create_table(table_name, columns)