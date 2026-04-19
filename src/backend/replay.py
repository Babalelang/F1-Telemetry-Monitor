# src/backend/replay.py
# Builds per-frame position data for the race replay.
# Each frame = one timestamp sample, contains x/y/speed/gear/tyre for every driver.

import numpy as np
import pandas as pd


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
    Returns a dict ready to JSON-serialise for dcc.Store.

    sample_rate: keep every Nth position sample (default 8 = ~4 Hz from 0.5 s data)

    Returns:
        {
          "track_x": [...],   # normalised track outline X
          "track_y": [...],
          "frames":  [        # list of frame dicts
            {
              "t": 12.5,          # race time seconds
              "lap": 1,
              "drivers": {
                "VER": {"x": .., "y": .., "speed": .., "gear": .., "tyre": "SOFT", "color": "#...", "pos": 1},
                ...
              }
            }, ...
          ],
          "total_frames": N,
          "drivers": ["VER", "HAM", ...],
          "total_laps": 57,
        }
    """

    # ── 1. Get track outline from the fastest lap ──────────────────────────
    try:
        fastest = session.laps.pick_fastest()
        pos_data = fastest.get_pos_data().add_distance()
        raw_x = pos_data["X"].values.tolist()
        raw_y = pos_data["Y"].values.tolist()
    except Exception:
        raw_x, raw_y = [], []

    track_x, track_y = _normalise_track(raw_x, raw_y)

    # ── 2. Collect position data per driver ───────────────────────────────
    drivers_in_session = session.laps["Driver"].dropna().unique().tolist()

    # Build a time-indexed DataFrame per driver: columns = [X, Y, Speed, nGear, Compound]
    driver_frames: dict = {}

    for drv in drivers_in_session:
        try:
            drv_laps = session.laps.pick_drivers(drv)
            pos  = session.pos_data[drv][["SessionTime","X","Y"]].copy()
            car  = session.car_data[drv][["SessionTime","Speed","nGear"]].copy()
            merged = pd.merge_asof(
                pos.sort_values("SessionTime"),
                car.sort_values("SessionTime"),
                on="SessionTime", direction="nearest"
            )
            merged = merged.iloc[::sample_rate].reset_index(drop=True)
            merged["t"] = merged["SessionTime"].dt.total_seconds()
            # Attach tyre compound per row via lap matching
            merged["Compound"] = _map_compound(merged["t"], drv_laps)
            driver_frames[drv] = merged
        except Exception:
            pass

    if not driver_frames:
        return None

    # ── 3. Build unified time axis ─────────────────────────────────────────
    # Use the driver with the most frames as the time spine
    spine_drv = max(driver_frames, key=lambda d: len(driver_frames[d]))
    time_axis = driver_frames[spine_drv]["t"].values

    # Total laps
    try:
        total_laps = int(session.laps["LapNumber"].max())
    except Exception:
        total_laps = 0

    # ── 4. Assemble frames ─────────────────────────────────────────────────
    frames = []
    # Keep only every Nth time point so the JSON stays manageable
    stride = max(1, len(time_axis) // 3000)  # cap at ~3000 frames

    for i, t in enumerate(time_axis[::stride]):
        frame_drivers = {}
        for drv, df in driver_frames.items():
            # Find nearest row
            idx = (df["t"] - t).abs().idxmin()
            row = df.iloc[idx]
            nx, ny = _normalise_point(float(row["X"]), float(row["Y"]), raw_x, raw_y)
            frame_drivers[drv] = {
                "x":     round(nx, 4),
                "y":     round(ny, 4),
                "speed": int(row.get("Speed", 0) or 0),
                "gear":  int(row.get("nGear", 0) or 0),
                "tyre":  str(row.get("Compound", "")) or "UNKNOWN",
                "color": TEAM_COLORS.get(drv, "#888888"),
            }
        # Approximate lap number from time
        try:
            lap_now = int(
                session.laps[session.laps["LapStartTime"].dt.total_seconds() <= t]["LapNumber"].max()
            )
        except Exception:
            lap_now = 1

        frames.append({"t": round(float(t), 1), "lap": lap_now, "drivers": frame_drivers})

    return {
        "track_x":     track_x,
        "track_y":     track_y,
        "frames":      frames,
        "total_frames": len(frames),
        "drivers":     list(driver_frames.keys()),
        "total_laps":  total_laps,
    }


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