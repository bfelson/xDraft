import pandas as pd
import sqlite3
from typing import Dict, List
import datetime

DB_FILE = "xDraft_database.db"

def initialize_db():
# Initializes the database if tables do not exist
    with sqlite3.connect(DB_FILE) as con:
        c = con.cursor()

        # Create hitters table
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS hitters (
                name TEXT PRIMARY KEY,
                PA  INTEGER,
                BA REAL,
                xBA REAL,
                "xBA-BA" REAL,
                SLG REAL,
                xSLG REAL,
                "xSLG-SLG" REAL,
                wOBA REAL,
                xwOBA REAL,
                "xwOBA-wOBA" REAL,
                POSITIONS TEXT
            )
            '''
        )

        # Create pitchers table
        c.execute('''
            CREATE TABLE IF NOT EXISTS pitchers (
                name TEXT PRIMARY KEY,
                PA INTEGER,
                BA REAL,
                xBA REAL,
                "xBA-BA" REAL,
                SLG REAL,
                xSLG REAL,
                "xSLG-SLG" REAL,
                wOBA REAL,
                xwOBA REAL,
                "xwOBA-wOBA" REAL,
                ERA REAL,
                xERA REAL,
                "ERA-xERA" REAL
            )
        ''')

        # Metadata table if we need it
        c.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

def save_data(df, table_name):
    with sqlite3.connect(DB_FILE) as con:
        df.to_sql(table_name, con, if_exists="replace")

def load_data(table_name):
    with sqlite3.connect(DB_FILE) as con:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con, index_col="name")
    return df

def update_last_updated(key: str = "last_updated"):
    now = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("REPLACE INTO metadata (key, value) VALUES (?, ?)", (key, now))

def get_last_updated(key: str = "last_updated") -> str:
    with sqlite3.connect(DB_FILE) as con:
        row = con.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
    return row[0] if row else "Never"