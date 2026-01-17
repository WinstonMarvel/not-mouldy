import time
from typing import Dict, List, Union, Any
import sqlite3
import rx

from rx import operators as ops
import statistics
from .db import write_to_db
from .sensor import read_sensor, init_sensor

if __name__ == "__main__":

    dht = init_sensor()
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
    ).subscribe(lambda entry: write_to_db(entry))

    print("Successful started humidity health score logger.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        dht.exit()
        connection.close()
