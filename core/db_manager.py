import sqlite3
import pandas as pd
import os

DB_PATH = "datachat.db"

def load_csv(file):
    """Loads uploaded CSV into SQLite and returns the dataframe."""
    df = pd.read_csv(file, encoding="latin-1")
    df.columns = (df.columns.str.strip()
                            .str.lower()
                            .str.replace(" ", "_")
                            .str.replace("-", "_")
                            .str.replace("/", "_"))
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("data", conn, if_exists="replace", index=False)
    conn.close()
    return df

def get_schema():
    """Returns schema of the loaded table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(data)")
    columns = cursor.fetchall()
    conn.close()
    schema = "Table: data\nColumns:\n"
    for col in columns:
        schema += f"  - {col[1]} ({col[2]})\n"
    return schema

def db_exists():
    """Checks if a database has been loaded."""
    return os.path.exists(DB_PATH)