# Humidity Health Score

A Raspberry Pi temperature and humidity monitoring system that reads from a DHT11 sensor every 15 seconds and logs 3-minute averaged readings to a SQLite database.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
./run.sh
```

This starts the Docker Compose stack in the background. The sensor process reads every 15 seconds, stores 3-minute averages in `/var/lib/grafana/sqlite/humidity.db`, and restarts automatically if the container exits.

The Docker deployment keeps only `180` days of readings by default and retries sensor initialization every `30` seconds instead of crash-looping if GPIO or the sensor is temporarily unavailable. Container logs are retained through Docker's capped log driver; file logging is still supported, but now opt-in via `LOG_TO_FILE=1`.

## Grafana Setup

Follow the instructions to [Install](https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/) Grafana.

Enable the Grafana server:

```bash
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Set up database permissions so Grafana can access the SQLite database:

```bash
sudo chown grafana:grafana climate.db
sudo chmod 777 /var/lib/grafana/sqlite
sudo chmod 666 /var/lib/grafana/sqlite/humidity.db
```

If you need to restart Grafana after configuration changes:

```bash
sudo systemctl restart grafana-server
```

Grafana will be available at `http://raspberrypi.local:3000` (default credentials: admin/admin).

Import `grafana-dashboard.json`.
