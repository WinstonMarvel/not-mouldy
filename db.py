connection = sqlite3.connect(
    "/var/lib/grafana/sqlite/humidity.db", check_same_thread=False
)
cursor = connection.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS humidity_data (timestamp INTEGER PRIMARY KEY, temperature REAL, humidity REAL)"
)


def write_to_db(entry):
    try:
        cursor.execute(
            "INSERT INTO humidity_data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
            (entry["timestamp"], entry["temperature"], entry["humidity"]),
        )
        connection.commit()
    except Exception as e:
        print("Something went wrong while writing to DB:", e)
