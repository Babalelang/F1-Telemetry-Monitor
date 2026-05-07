# loader.py — FastF1 data access with intelligent caching

import fastf1
import numpy as np
import threading

fastf1.Cache.enable_cache('./cache')

_SESSION_CACHE: dict = {}
_CACHE_LOCK = threading.Lock()


def load_session(year, gp, session_type, telemetry=True):
    """Load and cache a session. Subsequent calls return cached version."""
    key = f"{year}|{gp}|{session_type}"
    with _CACHE_LOCK:
        if key not in _SESSION_CACHE:
            session = fastf1.get_session(year, gp, session_type)
            session.load(
                telemetry=telemetry,
                laps=True,
                weather=True,
                messages=False,
            )
            _SESSION_CACHE[key] = session
        return _SESSION_CACHE[key]


def get_telemetry(lap):
    return lap.get_car_data().add_distance()


def get_weather(session):
    return session.weather_data


def clear_cache():
    with _CACHE_LOCK:
        _SESSION_CACHE.clear()

