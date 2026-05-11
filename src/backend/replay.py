"""
Drop-in replacement for _build_replay_data() in callbacks.py.
Key fixes:
  1. Consistent normalisation — track_x/y and all driver positions share
     the SAME min/max so they align perfectly on the canvas.
  2. Gap detection — frames where a driver teleports more than MAX_JUMP
     units get their position set to None so the JS skips trail drawing.
  3. Finer sampling (SAMPLE=4) for smoother motion with minimal data overhead.
  4. Speed sourced correctly via merge_asof so leaderboard order is real.
"""

import numpy as np
import pandas as pd
import threading

_REPLAY_CACHE: dict = {}
_REPLAY_CACHE_LOCK = threading.Lock()

TEAM_COLORS = {
    "VER": "#3671C6", "PER": "#3671C6",
    "HAM": "#27F4D2", "RUS": "#27F4D2",
    "LEC": "#E8002D", "SAI": "#E8002D",
    "NOR": "#FF8000", "PIA": "#FF8000",
    "ALO": "#358C75", "STR": "#358C75",
    "OCO": "#FF87BC", "GAS": "#FF87BC",
    "ALB": "#64C4FF", "SAR": "#64C4FF",
    "TSU": "#5E8FAA", "LAW": "#5E8FAA", "HAD": "#5E8FAA",
    "HUL": "#B6BABD", "MAG": "#B6BABD", "BOR": "#B6BABD",
    "BOT": "#00E701", "ZHO": "#00E701",
    "ANT": "#27F4D2", "DOO": "#FF8000",
    "BEA": "#E8002D", "COL": "#64C4FF",
}

# Maximum normalised-unit jump between consecutive frames before we
# treat it as a teleport (pit entry, data gap, lap restart).
MAX_JUMP = 0.08
SAMPLE   = 4     # take every Nth position row — finer than old SAMPLE=8
MAX_FRAMES = 1200


def _build_replay_data(session, max_frames: int = MAX_FRAMES):
    cache_key = f"{session.event['EventName']}_{session.event['EventDate']}"
    with _REPLAY_CACHE_LOCK:
        if cache_key in _REPLAY_CACHE:
            return _REPLAY_CACHE[cache_key]

    # ── 1. Track outline from fastest lap ─────────────────────────────────────
    try:
        fp = session.laps.pick_fastest().get_pos_data()
        raw_tx = fp["X"].values.astype(float).tolist()
        raw_ty = fp["Y"].values.astype(float).tolist()
    except Exception:
        raw_tx, raw_ty = [], []

    # ── 2. Build driver-number → abbreviation map ─────────────────────────────
    try:
        car_map = (session.laps[["Driver", "DriverNumber"]]
                   .dropna().drop_duplicates("Driver"))
        drv_to_car = {r.Driver: str(int(r.DriverNumber))
                      if not isinstance(r.DriverNumber, str)
                      else str(r.DriverNumber)
                      for r in car_map.itertuples()}
    except Exception:
        drv_to_car = {}

    drivers = sorted(session.laps["Driver"].dropna().unique().tolist())

    # ── 3. Load position & speed for each driver ──────────────────────────────
    drv_pos: dict[str, pd.DataFrame]   = {}   # cols: _t, x, y
    drv_spd: dict[str, np.ndarray]     = {}   # shape (N, 2): [_t, speed]

    for drv in drivers:
        car_key = drv_to_car.get(drv, drv)
        # Try string variations
        if session.pos_data:
            if car_key not in session.pos_data:
                car_key = next((k for k in session.pos_data
                                if str(k) == str(car_key)), None)
        if not car_key or not session.pos_data or car_key not in session.pos_data:
            continue

        try:
            pos_df = session.pos_data[car_key][["SessionTime", "X", "Y"]].copy()
            pos_df["_t"] = pos_df["SessionTime"].dt.total_seconds()
            pos_df = (pos_df[["_t", "X", "Y"]].dropna()
                      .sort_values("_t").iloc[::SAMPLE].reset_index(drop=True))
            if len(pos_df) < 5:
                continue
            drv_pos[drv] = pos_df.rename(columns={"X": "x", "Y": "y"})
        except Exception:
            continue

        try:
            if session.car_data and car_key in session.car_data:
                cd = session.car_data[car_key][["SessionTime", "Speed"]].copy()
                cd["_t"] = cd["SessionTime"].dt.total_seconds()
                cd = cd[["_t", "Speed"]].dropna().sort_values("_t")
                drv_spd[drv] = cd.values
        except Exception:
            pass

    if not drv_pos:
        return None

    # ── 4. Collect ALL raw coordinates for a single normalisation ─────────────
    all_x, all_y = [], []
    if raw_tx:
        all_x.extend(raw_tx); all_y.extend(raw_ty)
    for df in drv_pos.values():
        all_x.extend(df["x"].tolist()); all_y.extend(df["y"].tolist())

    mn_x, mx_x = float(min(all_x)), float(max(all_x))
    mn_y, mx_y = float(min(all_y)), float(max(all_y))
    rng = max(mx_x - mn_x, mx_y - mn_y) or 1.0

    def _nx(v): return round((float(v) - mn_x) / rng, 5)
    def _ny(v): return round((float(v) - mn_y) / rng, 5)

    # Normalise track
    track_nx = [_nx(v) for v in raw_tx]
    track_ny = [_ny(v) for v in raw_ty]

    # Normalise driver positions & compute previous position for gap detection
    drv_norm: dict[str, np.ndarray] = {}  # shape (N, 3): [_t, nx, ny]
    for drv, df in drv_pos.items():
        nx = np.array([_nx(v) for v in df["x"]])
        ny = np.array([_ny(v) for v in df["y"]])
        drv_norm[drv] = np.column_stack([df["_t"].values, nx, ny])

    # ── 5. Build time axis ─────────────────────────────────────────────────────
    spine = max(drv_norm, key=lambda d: len(drv_norm[d]))
    t_vals = drv_norm[spine][:, 0]
    stride = max(1, len(t_vals) // max_frames)
    t_axis = t_vals[::stride]

    # ── 6. Build frames ────────────────────────────────────────────────────────
    # Cache sorted time arrays for fast searchsorted
    drv_t    = {d: arr[:, 0] for d, arr in drv_norm.items()}
    drv_prev = {d: None for d in drv_norm}   # last known normalised pos

    frames = []
    for t in t_axis:
        fd = {}
        for drv, arr in drv_norm.items():
            idx = int(np.searchsorted(drv_t[drv], t))
            idx = min(idx, len(arr) - 1)
            nx, ny = float(arr[idx, 1]), float(arr[idx, 2])

            # Gap detection: if the driver jumped too far, treat position
            # as None so JS knows to break the trail.
            prev = drv_prev[drv]
            if prev is not None:
                dx, dy = nx - prev[0], ny - prev[1]
                jump = (dx*dx + dy*dy) ** 0.5
                if jump > MAX_JUMP:
                    # Mark as teleport — JS will skip trail for this frame
                    fd[drv] = None
                    drv_prev[drv] = (nx, ny)   # update so next frame is clean
                    continue

            # Speed lookup
            speed = 0
            if drv in drv_spd:
                sarr = drv_spd[drv]
                si = int(np.searchsorted(sarr[:, 0], t))
                si = min(si, len(sarr) - 1)
                speed = int(sarr[si, 1])

            fd[drv] = {"x": nx, "y": ny, "speed": speed}
            drv_prev[drv] = (nx, ny)

        frames.append({"t": round(float(t), 1), "d": fd})

    try:
        total_laps = int(session.laps["LapNumber"].max())
    except Exception:
        total_laps = 0

    result = {
        "track_x":    track_nx,
        "track_y":    track_ny,
        "frames":     frames,
        "total":      len(frames),
        "drivers":    list(drv_norm.keys()),
        "colors":     {d: TEAM_COLORS.get(d, "#888888") for d in drv_norm},
        "total_laps": total_laps,
    }

    with _REPLAY_CACHE_LOCK:
        _REPLAY_CACHE[cache_key] = result
    return result