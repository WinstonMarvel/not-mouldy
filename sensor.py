import logging
from typing import Optional, Dict, Union
import adafruit_dht
import board

logger = logging.getLogger(__name__)


"""
Initialize the DHT11 sensor on the specified pin.
"""


def init_sensor(pin=board.D4) -> adafruit_dht.DHT11:
    dht = adafruit_dht.DHT11(board.D4)
    return dht


"""
Read temperature and humidity from the DHT11 sensor.
Returns a dict with keys: temperature, humidity
or None if reading failed.
"""


def read_sensor(dht: adafruit_dht.DHT11) -> Optional[Dict[str, float]]:
    try:
        # Read both values in quick succession to avoid double sensor reads
        temp = dht.temperature
        hum = dht.humidity
        if temp is not None and hum is not None:
            return {"temperature": temp, "humidity": hum}
    except RuntimeError as e:
        # DHT11 read failures are expected noise (~30-50% of reads), not errors
        logger.debug("Sensor read noise (expected): %s", e)
    return None
