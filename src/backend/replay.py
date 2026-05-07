# src/backend/replay.py
# Builds per-frame position data for the race replay.
# Each frame = one timestamp sample, contains x/y/speed/gear/tyre for every driver.

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import hashlib
import os
import pickle


TEAM_COLORS = {
    "VER": "#3671C6", "PER": "#3671C6",
    "HAM": "#27F4D2", "RUS": "#27F4D2",
    "LEC": "#E8002D", "SAI": "#E8002D",
    "NOR": "#FF8000", "PIA": "#FF8000",
    "ALO": "#358C75", "STR": "#358C75",
    "OCO": "#FF87BC", "GAS": "#FF87BC",
    "ALB": "#64C4FF", "SAR": "#64C4FF",
    "TSU": "#5E8FAA", "RIC": "#5E8FAA",
    "HUL": "#B6BABD", "MAG": "#B6BABD",
    "BOT": "#00E701", "ZHO": "#00E701",
    "BEA": "#3671C6", "ANT": "#27F4D2",
    "LAW": "#5E8FAA", "HAD": "#5E8FAA",
    "DOO": "#FF8000", "BOR": "#B6BABD",
}


def build_replay_frames(session, sample_rate: int = 8):
    """
    Optimized version of build_replay_frames with caching and parallel processing.
    """
    # Generate a cache key based on session ID and sample rate
    session_id = session.event['EventName'] + str(session.event['EventDate'])
    cache_key = hashlib.md5(f"{session_id}_{sample_rate}".encode()).hexdigest()
    cache_file = os.path.join("cache", f"replay_{cache_key}.pkl")

    # Check if cached data exists
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    # ── 1. Get track outline from the fastest lap ──────────────────────────
    try:
        fastest = session.laps.pick_fastest()
        pos_data = fastest.get_pos_data().add_distance()
        raw_x = pos_data["X"].values.tolist()
        raw_y = pos_data["Y"].values.tolist()
    except Exception:
        raw_x, raw_y = [], []

    # ── 2. Process frames in parallel ──────────────────────────────────────
    def process_frame(frame):
        return {
            "t": frame.Time,
            "lap": frame.LapNumber,
            "drivers": {
                driver: {
                    "x": frame.PosX,
                    "y": frame.PosY,
                    "speed": frame.Speed,
                    "gear": frame.Gear,
                    "tyre": frame.Tyre,
                    "color": TEAM_COLORS.get(driver, "#888888"),
                    "pos": frame.Position,
                }
                for driver in frame.Drivers
            },
        }

    frames = Parallel(n_jobs=-1)(delayed(process_frame)(frame) for frame in session.frames)

    # ── 3. Build final data structure ──────────────────────────────────────
    replay_data = {
        "track_x": raw_x,
        "track_y": raw_y,
        "frames": frames,
        "total_frames": len(frames),
        "drivers": list(TEAM_COLORS.keys()),
        "total_laps": session.laps[-1].LapNumber if session.laps else 0,
    }

    # Cache the result
    with open(cache_file, "wb") as f:
        pickle.dump(replay_data, f)

    return replay_data


def _map_compound(times_sec, drv_laps):
    """Return a Series of compound names aligned to times_sec."""
    result = ["UNKNOWN"] * len(times_sec)
    try:
        for _, lap in drv_laps.iterrows():
            start = lap["LapStartTime"].total_seconds() if hasattr(lap["LapStartTime"], "total_seconds") else 0
            end   = start + (lap["LapTime"].total_seconds() if pd.notna(lap["LapTime"]) else 120)
            comp  = lap.get("Compound", "UNKNOWN") or "UNKNOWN"
            for i, t in enumerate(times_sec):
                if start <= t <= end:
                    result[i] = comp
    except Exception:
        pass
    return result


def _normalise_track(raw_x, raw_y):
    """Normalise track coordinates to 0–1 range."""
    if not raw_x:
        return [], []
    mn_x, mx_x = min(raw_x), max(raw_x)
    mn_y, mx_y = min(raw_y), max(raw_y)
    rng = max(mx_x - mn_x, mx_y - mn_y) or 1
    nx = [round((x - mn_x) / rng, 4) for x in raw_x]
    ny = [round((y - mn_y) / rng, 4) for y in raw_y]
    return nx, ny


def _normalise_point(x, y, raw_x, raw_y):
    if not raw_x:
        return 0.5, 0.5
    mn_x, mx_x = min(raw_x), max(raw_x)
    mn_y, mx_y = min(raw_y), max(raw_y)
    rng = max(mx_x - mn_x, mx_y - mn_y) or 1
    return (x - mn_x) / rng, (y - mn_y) / rng