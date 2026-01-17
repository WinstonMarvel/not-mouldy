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

The script will run in the background using nohup, continuously monitoring temperature and humidity, averaging readings every 3 minutes and storing them in `climate.db`.

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
