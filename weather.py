import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional

logger = logging.getLogger(__name__)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OUTDOOR_WEATHER_PROVIDER = os.environ.get("OUTDOOR_WEATHER_PROVIDER", "open-meteo")
OUTDOOR_WEATHER_LATITUDE = os.environ.get("OUTDOOR_WEATHER_LATITUDE", "").strip()
OUTDOOR_WEATHER_LONGITUDE = os.environ.get("OUTDOOR_WEATHER_LONGITUDE", "").strip()
OUTDOOR_WEATHER_POSTAL_CODE = os.environ.get("OUTDOOR_WEATHER_POSTAL_CODE", "").strip()
OUTDOOR_WEATHER_COUNTRY_CODE = os.environ.get(
    "OUTDOOR_WEATHER_COUNTRY_CODE", "DE"
).strip()
OUTDOOR_WEATHER_POLL_SECONDS = max(
    int(os.environ.get("OUTDOOR_WEATHER_POLL_SECONDS", "900")), 0
)


def _get_json(url: str, params: Dict[str, str]) -> Dict:
    query = urllib.parse.urlencode(params)
    request_url = f"{url}?{query}"
    with urllib.request.urlopen(request_url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


class OutdoorWeatherClient:
    def __init__(self) -> None:
        self._resolved_coordinates: Optional[Dict[str, float]] = None
        self._last_fetch_at = 0.0
        self._last_reading: Optional[Dict[str, float]] = None
        self._config_error_logged = False

    def is_enabled(self) -> bool:
        return OUTDOOR_WEATHER_PROVIDER == "open-meteo" and bool(
            (OUTDOOR_WEATHER_LATITUDE and OUTDOOR_WEATHER_LONGITUDE)
            or OUTDOOR_WEATHER_POSTAL_CODE
        )

    def get_current_reading(self) -> Optional[Dict[str, float]]:
        if not self.is_enabled():
            if not self._config_error_logged:
                logger.info(
                    "Outdoor weather disabled; set OUTDOOR_WEATHER_LATITUDE/OUTDOOR_WEATHER_LONGITUDE or OUTDOOR_WEATHER_POSTAL_CODE"
                )
                self._config_error_logged = True
            return None

        now = time.time()
        if (
            self._last_reading is not None
            and OUTDOOR_WEATHER_POLL_SECONDS > 0
            and now - self._last_fetch_at < OUTDOOR_WEATHER_POLL_SECONDS
        ):
            return self._last_reading

        try:
            coordinates = self._resolve_coordinates()
            response = _get_json(
                FORECAST_URL,
                {
                    "latitude": str(coordinates["latitude"]),
                    "longitude": str(coordinates["longitude"]),
                    "current": "temperature_2m,relative_humidity_2m",
                    "timezone": "auto",
                },
            )
            current = response.get("current", {})
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            if temperature is None or humidity is None:
                raise ValueError("Open-Meteo response missing current conditions")

            self._last_reading = {
                "outdoor_temperature": float(temperature),
                "outdoor_humidity": float(humidity),
            }
            self._last_fetch_at = now
            return self._last_reading
        except (OSError, ValueError, urllib.error.URLError) as e:
            logger.warning("Failed to fetch outdoor weather: %s", e)
            return self._last_reading

    def _resolve_coordinates(self) -> Dict[str, float]:
        if self._resolved_coordinates is not None:
            return self._resolved_coordinates

        if OUTDOOR_WEATHER_LATITUDE and OUTDOOR_WEATHER_LONGITUDE:
            self._resolved_coordinates = {
                "latitude": float(OUTDOOR_WEATHER_LATITUDE),
                "longitude": float(OUTDOOR_WEATHER_LONGITUDE),
            }
            return self._resolved_coordinates

        if not OUTDOOR_WEATHER_POSTAL_CODE:
            raise ValueError("Outdoor weather location is not configured")

        response = _get_json(
            GEOCODING_URL,
            {
                "name": OUTDOOR_WEATHER_POSTAL_CODE,
                "count": "1",
                "language": "en",
                "format": "json",
                "countryCode": OUTDOOR_WEATHER_COUNTRY_CODE,
            },
        )
        results = response.get("results", [])
        if not results:
            raise ValueError("No geocoding result for configured postal code")

        first_result = results[0]
        self._resolved_coordinates = {
            "latitude": float(first_result["latitude"]),
            "longitude": float(first_result["longitude"]),
        }
        logger.info(
            "Resolved outdoor weather location to %.4f, %.4f",
            self._resolved_coordinates["latitude"],
            self._resolved_coordinates["longitude"],
        )
        return self._resolved_coordinates