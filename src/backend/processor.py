# processor.py — Lap filtering, tyre analysis, stint strategy, and delta computations

import numpy as np
import pandas as pd


# ── Basic lap retrieval ────────────────────────────────────────────────────────

def get_driver_lap(session, driver, lap_choice):
    """Return a specific lap or fastest lap for a driver."""
    driver_laps = session.laps.pick_drivers(driver)
    if lap_choice == "f":
        return driver_laps.pick_fastest()
    else:
        filtered = driver_laps[driver_laps["LapNumber"] == int(lap_choice)]
        if filtered.empty:
            raise ValueError(f"Lap {lap_choice} not found for {driver}")
        return filtered.iloc[0]


# ── Lap time stats ─────────────────────────────────────────────────────────────

def lap_time_analysis(session, driver):
    laps = session.laps.pick_drivers(driver)
    lap_times = laps["LapTime"].dt.total_seconds().dropna()
    return {
        "best_lap":        float(lap_times.min()),
        "average_lap":     float(lap_times.mean()),
        "consistency_std": float(lap_times.std()),
        "worst_lap":       float(lap_times.max()),
    }


def sector_time_analysis(session, driver):
    laps = session.laps.pick_drivers(driver)
    return {
        "sector1_avg": laps["Sector1Time"].mean(),
        "sector2_avg": laps["Sector2Time"].mean(),
        "sector3_avg": laps["Sector3Time"].mean(),
    }


# ── Compound summary ──────────────────────────────────────────────────────────

def get_compound_summary(laps):
    compounds = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
    return {c: len(laps.pick_compounds(c)) for c in compounds}


# ── Tyre degradation curves ────────────────────────────────────────────────────

def tyre_degradation(session, driver):
    """
    Build a smooth tyre degradation dataset per stint.
    Returns a list of dicts: {stint, compound, laps[], lap_times_s[]}
    Filters out laps with pit stops, safety car, etc. using 107% rule.
    """
    laps = session.laps.pick_drivers(driver).copy()
    laps["LapTimeSec"] = laps["LapTime"].dt.total_seconds()
    laps = laps.dropna(subset=["LapTimeSec", "Stint", "Compound"])
    laps = laps[laps["PitOutTime"].isna() & laps["PitInTime"].isna()]

    # Apply 107% filter relative to each stint's median
    stints = []
    for (stint_num, compound), grp in laps.groupby(["Stint", "Compound"]):
        grp = grp.sort_values("LapNumber").reset_index(drop=True)
        if len(grp) < 2:
            continue
        median_t = grp["LapTimeSec"].median()
        clean = grp[grp["LapTimeSec"] < median_t * 1.07]
        if len(clean) < 2:
            clean = grp
        # TyreLife: laps on this set (1-based)
        tyre_life = clean["TyreLife"].values if "TyreLife" in clean.columns else np.arange(1, len(clean) + 1)
        stints.append({
            "stint":     int(stint_num),
            "compound":  str(compound),
            "tyre_life": tyre_life.tolist(),
            "lap_times": clean["LapTimeSec"].values.tolist(),
            "lap_nums":  clean["LapNumber"].values.tolist(),
        })
    return stints


# ── Stint strategy ────────────────────────────────────────────────────────────

def stint_strategy(session):
    """
    Build a per-driver stint strategy table for the entire session.
    Returns list of {driver, stints: [{compound, start_lap, end_lap, tyre_life}]}
    Sorted by finishing position where available.
    """
    laps = session.laps.copy()
    laps = laps.dropna(subset=["Driver", "Stint", "Compound", "LapNumber"])

    results = []
    for driver, drv_laps in laps.groupby("Driver"):
        drv_laps = drv_laps.sort_values("LapNumber")
        driver_stints = []
        for (stint_num, compound), grp in drv_laps.groupby(["Stint", "Compound"]):
            grp = grp.sort_values("LapNumber")
            tyre_age = grp["TyreLife"].max() if "TyreLife" in grp.columns else None
            driver_stints.append({
                "stint":      int(stint_num),
                "compound":   str(compound),
                "start_lap":  int(grp["LapNumber"].min()),
                "end_lap":    int(grp["LapNumber"].max()),
                "laps":       int(len(grp)),
                "tyre_age":   int(tyre_age) if tyre_age and not np.isnan(float(tyre_age)) else None,
            })
        driver_stints.sort(key=lambda x: x["start_lap"])
        results.append({"driver": driver, "stints": driver_stints})

    # Try to sort by finishing position
    try:
        pos_map = {}
        for driver, drv_laps in laps.groupby("Driver"):
            pos = drv_laps["Position"].dropna().iloc[-1] if "Position" in drv_laps.columns else 99
            pos_map[driver] = int(pos) if pos else 99
        results.sort(key=lambda x: pos_map.get(x["driver"], 99))
    except Exception:
        results.sort(key=lambda x: x["driver"])

    return results


# ── Lap delta computation ─────────────────────────────────────────────────────

def compute_lap_delta(lap1, lap2):
    """
    Compute signed time delta between two laps at every distance point.
    Returns (distance_array, delta_array_seconds) — positive = lap1 is ahead.
    """
    try:
        t1 = lap1.get_car_data().add_distance()
        t2 = lap2.get_car_data().add_distance()

        t1 = t1[["Distance", "SessionTime"]].dropna().sort_values("Distance")
        t2 = t2[["Distance", "SessionTime"]].dropna().sort_values("Distance")

        # Common distance grid
        d_min = max(t1["Distance"].iloc[0],  t2["Distance"].iloc[0])
        d_max = min(t1["Distance"].iloc[-1], t2["Distance"].iloc[-1])
        dist_grid = np.linspace(d_min, d_max, 500)

        t1_interp = np.interp(dist_grid,
                               t1["Distance"].values,
                               t1["SessionTime"].dt.total_seconds().values)
        t2_interp = np.interp(dist_grid,
                               t2["Distance"].values,
                               t2["SessionTime"].dt.total_seconds().values)

        # Normalise to 0 at start
        t1_interp -= t1_interp[0]
        t2_interp -= t2_interp[0]

        delta = t1_interp - t2_interp  # positive = lap1 faster at that point
        return dist_grid.tolist(), delta.tolist()
    except Exception:
        return [], []


# ── Other helpers ─────────────────────────────────────────────────────────────

def get_fastest_lap(session, driver):
    return session.laps.pick_drivers(driver).pick_fastest()


def compare_telemetry(lap1, lap2):
    t1 = lap1.get_car_data().add_distance()
    t2 = lap2.get_car_data().add_distance()
    return t1, t2


def tyre_stint_analysis(session, driver):
    laps = session.laps.pick_drivers(driver)
    return laps.groupby(["Stint", "Compound"])["TyreLife"].max()


def speed_zones(lap):
    telemetry = lap.get_car_data().add_distance()
    braking      = telemetry[telemetry["Brake"] > 0]
    full_throttle = telemetry[telemetry["Throttle"] > 90]
    cornering    = telemetry[(telemetry["Speed"] < 120) & (telemetry["Brake"] == False)]
    return {
        "braking_points":  len(braking),
        "high_speed_zones": len(full_throttle),
        "cornering_zones": len(cornering),
    }

