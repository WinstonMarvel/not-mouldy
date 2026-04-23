import logging
import os
import sqlite3
from typing import Dict, Union

logger = logging.getLogger(__name__)

DB_PATH = "/var/lib/grafana/sqlite/humidity.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

connection = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS humidity_data (timestamp INTEGER PRIMARY KEY, temperature REAL, humidity REAL)"
)


"""
Write a single entry to the SQLite database.
Entry is a dict with keys: timestamp, temperature, humidity
"""


def write_to_db(entry: Dict[str, Union[int, float]]) -> None:
    try:
        cursor.execute(
            "INSERT INTO humidity_data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
            (entry["timestamp"], entry["temperature"], entry["humidity"]),
        )
        connection.commit()
    except Exception as e:
        logger.error("Failed to write to DB: %s", e)


def close_db() -> None:
    connection.close()
