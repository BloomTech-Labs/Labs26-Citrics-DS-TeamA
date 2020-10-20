# development/utilities/db_sentry.py

from database import PostgreSQL
from termcolor import colored
from datetime import datetime

import pandas as pd
import time

# Run this script to monitor connections to database ...

# Program will scan for connections in 5 minute intervals
# and terminate disruptive connections. Deliberate connections
# should remain uninterrupted.

# Program will run in perpetuity until KeyBoard Interrupted.

while True:

    query = """
	SELECT *
	FROM pg_stat_activity
	WHERE datname='postgres'
	"""

    db = PostgreSQL()
    conn = db.connection
    cur = conn.cursor()
    cur.execute(query)

    result = pd.DataFrame.from_records(
        cur.fetchall(),
        columns=[
            "datid",
            "datname",
            "pid",
            "usesysid",
            "username",
            "application_name",
            "client_addr",
            "client_hostname",
            "client_port",
            "backend_start",
            "xact_start",
            "query_start",
            "state_change",
            "wait_event_type",
            "wait_event",
            "state",
            "backend_xid",
            "backend_xmin",
            "query",
            "backend_type"
        ]
    )

    num_connections = len(result) - 1

    print(f"\nCurrent Time: {str(datetime.now())}\n")
    print(colored(
        f"\nNumber of Current Connections: {num_connections}\n",
        "blue"))
    print(colored(
        f"\nConnected Addresses:\n{result.client_addr}\n",
        "blue"))

    conn.close()

    if num_connections >= 20:

        print(colored(
            "\nHIGH NUMBER OF CONNECTIONS ... PREPARING TO ENGAGE KILL SWITCH ...\n",
            "red"
        ))

        kill_switch = """
		SELECT
			pg_terminate_backend(pid)
		FROM
			pg_stat_get_activity(NULL::integer)
		WHERE
			datid = (
				SELECT
					oid
				FROM
					pg_database
				WHERE
					datname='postgres' AND client_addr='172.31.43.136');
		"""

        db = PostgreSQL()
        conn = db.connection
        cur = conn.cursor()

        def run_kill_switch():
            cur.execute(kill_switch)

            result = pd.DataFrame.from_records(
                cur.fetchall(),
                columns=["pg_terminate_backend"])

            if result.pg_terminate_backend[0] == True:
                print(colored(
                    "\nCULPRIT CONNECTIONS TERMINATED\n",
                    "green"))
            elif result.pg_terminate_backend[0] is None:
                print(colored(
                    "\nNO CULPRIT CONNECTIONS TO TERMINATE\n",
                    "blue"))
            else:
                print(colored(
                    "\nTERMINATION FAILED ... REATTEMPTING",
                    "red"))
                return run_kill_switch()

        run_kill_switch()

        conn.close()

    time.sleep(300)
