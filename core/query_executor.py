import sqlite3
import pandas as pd

DB_PATH = "datachat.db"

def run_query(sql):
    """
    Executes SQL and returns (success, dataframe or error string).
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return True, df
    except Exception as e:
        conn.close()
        return False, str(e)