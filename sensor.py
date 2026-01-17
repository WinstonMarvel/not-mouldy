from typing import Optional, Dict, Union
import adafruit_dht
import board

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
        print("Reading error:", e)
    return None
