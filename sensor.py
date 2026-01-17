import adafruit_dht
import board


def init_sensor(pin=board.D4):
    dht = adafruit_dht.DHT11(board.D4)
    return dht


def read_sensor(dht):
    try:
        # Read both values in quick succession to avoid double sensor reads
        temp = dht.temperature
        hum = dht.humidity
        if temp is not None and hum is not None:
            return {"temperature": temp, "humidity": hum}
    except RuntimeError as e:
        print("Reading error:", e)
    return None
