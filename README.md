# Humidity Health Score

A Raspberry Pi temperature and humidity monitoring system that reads from a DHT11 sensor every 15 seconds and logs 3-minute averaged readings to a SQLite database.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m humidity_health_score.main
```

The script will continuously monitor temperature and humidity, averaging readings every 3 minutes and storing them in the database.
