# comparator.py — align two drivers' telemetry for head-to-head

import pandas as pd


def compare_drivers(session, driver1, driver2):
    """
    Return (tel1, tel2, lap1, lap2) for the two drivers' fastest laps.
    Raises ValueError with a clear message if either driver has no usable lap.
    """
    laps1 = session.laps.pick_drivers(driver1)
    laps2 = session.laps.pick_drivers(driver2)

    if laps1.empty:
        raise ValueError(f"No laps found for {driver1}")
    if laps2.empty:
        raise ValueError(f"No laps found for {driver2}")

    lap1 = laps1.pick_fastest()
    lap2 = laps2.pick_fastest()

    # pick_fastest() can return None or an empty Series — guard both
    if lap1 is None or (hasattr(lap1, "empty") and lap1.empty):
        raise ValueError(f"No fastest lap available for {driver1}")
    if lap2 is None or (hasattr(lap2, "empty") and lap2.empty):
        raise ValueError(f"No fastest lap available for {driver2}")

    tel1 = lap1.get_car_data().add_distance()
    tel2 = lap2.get_car_data().add_distance()

    if tel1.empty:
        raise ValueError(f"No telemetry data for {driver1}")
    if tel2.empty:
        raise ValueError(f"No telemetry data for {driver2}")

    return tel1, tel2, lap1, lap2


def safe_sector(lap, sector_num):
    """
    Safely retrieve a sector time from a lap (pandas Series).
    Returns the timedelta or None — never raises.
    """
    key = f"Sector{sector_num}Time"
    try:
        val = lap[key] if key in lap.index else None
        if val is None:
            return None
        if pd.isnull(val):
            return None
        return val
    except Exception:
        return None