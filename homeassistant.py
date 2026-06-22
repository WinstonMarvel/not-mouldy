import json
import logging
import os
import urllib.error
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

HA_URL = os.environ.get("HA_URL", "").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
HA_ENABLED = bool(HA_URL and HA_TOKEN)

if HA_ENABLED:
    logger.info("Home Assistant integration enabled: pushing to %s", HA_URL)
else:
    logger.warning(
        "Home Assistant integration DISABLED (HA_URL=%r, HA_TOKEN=%s)",
        HA_URL,
        "set" if HA_TOKEN else "missing",
    )


def _push_state(entity_id: str, state: str, attributes: dict) -> None:
    url = f"{HA_URL}/api/states/{entity_id}"
    payload = json.dumps({"state": state, "attributes": attributes}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status not in (200, 201):
            raise RuntimeError(f"Unexpected HA response status: {resp.status}")


def push_indoor_reading(temperature: float, humidity: float) -> None:
    """Push indoor temperature and humidity to Home Assistant as sensor states."""
    if not HA_ENABLED:
        return

    try:
        _push_state(
            "sensor.not_mouldy_temperature",
            f"{temperature:.1f}",
            {
                "unit_of_measurement": "°C",
                "friendly_name": "Indoor Temperature",
                "device_class": "temperature",
                "state_class": "measurement",
            },
        )
        _push_state(
            "sensor.not_mouldy_humidity",
            f"{humidity:.1f}",
            {
                "unit_of_measurement": "%",
                "friendly_name": "Indoor Humidity",
                "device_class": "humidity",
                "state_class": "measurement",
            },
        )
        logger.debug(
            "Pushed to Home Assistant: temp=%.1f°C humidity=%.1f%%",
            temperature,
            humidity,
        )
    except urllib.error.URLError as exc:
        logger.error(
            "Home Assistant push failed (network) — check HA_URL=%r is reachable: %s",
            HA_URL,
            exc,
        )
    except Exception as exc:
        logger.error("Home Assistant push failed: %s", exc, exc_info=True)
