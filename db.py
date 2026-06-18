import logging
import os
import sqlite3
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

DB_PATH = "/var/lib/grafana/sqlite/humidity.db"
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "180"))
RETENTION_SECONDS = RETENTION_DAYS * 24 * 60 * 60
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

connection = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = connection.cursor()
last_prune_day = -1

cursor.execute(
    "CREATE TABLE IF NOT EXISTS humidity_data (timestamp INTEGER PRIMARY KEY, temperature REAL, humidity REAL, outdoor_temperature REAL, outdoor_humidity REAL)"
)

existing_columns = {
    row[1] for row in cursor.execute("PRAGMA table_info(humidity_data)").fetchall()
}
if "outdoor_temperature" not in existing_columns:
    cursor.execute("ALTER TABLE humidity_data ADD COLUMN outdoor_temperature REAL")
if "outdoor_humidity" not in existing_columns:
    cursor.execute("ALTER TABLE humidity_data ADD COLUMN outdoor_humidity REAL")
connection.commit()


def prune_old_data(current_timestamp: int) -> None:
    global last_prune_day

    if RETENTION_DAYS <= 0:
        return

    current_day = current_timestamp // (24 * 60 * 60)
    if current_day == last_prune_day:
        return

    cutoff_timestamp = current_timestamp - RETENTION_SECONDS
    cursor.execute(
        "DELETE FROM humidity_data WHERE timestamp < ?", (cutoff_timestamp,)
    )
    deleted_rows = cursor.rowcount
    connection.commit()
    last_prune_day = current_day

    if deleted_rows > 0:
        logger.info(
            "Pruned %s rows older than %s days", deleted_rows, RETENTION_DAYS
        )


"""
Write a single entry to the SQLite database.
Entry is a dict with keys: timestamp, temperature, humidity and optional outdoor values
"""


def write_to_db(entry: Dict[str, Union[int, float, None]]) -> None:
    try:
        prune_old_data(int(entry["timestamp"]))
        cursor.execute(
            "INSERT INTO humidity_data (timestamp, temperature, humidity, outdoor_temperature, outdoor_humidity) VALUES (?, ?, ?, ?, ?)",
            (
                entry["timestamp"],
                entry["temperature"],
                entry["humidity"],
                entry.get("outdoor_temperature"),
                entry.get("outdoor_humidity"),
            ),
        )
        connection.commit()
    except Exception as e:
        logger.error("Failed to write to DB: %s", e)


def close_db() -> None:
    connection.close()
