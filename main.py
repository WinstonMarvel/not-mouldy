import logging
import os
import time
from logging.handlers import RotatingFileHandler
import rx

from rx import operators as ops
import statistics
from db import write_to_db, close_db
from sensor import read_sensor, init_sensor

LOG_DIR = os.environ.get("LOG_DIR", "/app/logs")
LOG_TO_FILE = os.environ.get("LOG_TO_FILE", "0") == "1"
SENSOR_RETRY_DELAY_SECONDS = int(os.environ.get("SENSOR_RETRY_DELAY_SECONDS", "30"))
os.makedirs(LOG_DIR, exist_ok=True)

handlers = [logging.StreamHandler()]
if LOG_TO_FILE:
    handlers.insert(
        0,
        RotatingFileHandler(
            os.path.join(LOG_DIR, "app.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        ),
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)


def wait_for_sensor():
    while True:
        try:
            return init_sensor()
        except Exception:
            logger.exception(
                "Sensor initialization failed; retrying in %s seconds",
                SENSOR_RETRY_DELAY_SECONDS,
            )
            time.sleep(SENSOR_RETRY_DELAY_SECONDS)

if __name__ == "__main__":

    dht = wait_for_sensor()
    source = rx.interval(15).pipe(
        ops.map(lambda _: read_sensor(dht)), ops.filter(lambda x: x is not None)
    )

    source.pipe(
        ops.buffer_with_time(180),
        ops.filter(lambda buf: len(buf) > 0),
        ops.map(
            lambda buf: {
                "timestamp": int(
                    time.time() // 180 * 180
                ),  # // Floor division for 3 min interval start
                "temperature": statistics.mean(x["temperature"] for x in buf),
                "humidity": statistics.mean(x["humidity"] for x in buf),
            }
        ),
    ).subscribe(
        on_next=lambda entry: write_to_db(entry),
        on_error=lambda e: logger.error("Observable stream error: %s", e),
    )

    logger.info("Humidity health score logger started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        dht.exit()
        close_db()
