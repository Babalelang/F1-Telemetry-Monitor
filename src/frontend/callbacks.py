# callbacks.py — Premium F1 Telemetry Dashboard (optimized)
# -*- coding: utf-8 -*-
"""Improvements:
  - Replay animates smoothly: fewer frames + multi-step advance per tick
  - Loading spinner removed (non-blocking)
  - Analysis module cards link to tabs
  - Dropdown styling via CSS only
"""

from dash import Input, Output, State, ctx, no_update, ALL
from dash import html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os, threading, time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import fastf1
fastf1.Cache.enable_cache("./cache")

from src.backend.processor import lap_time_analysis
from src.backend.comparator import compare_drivers
from src.frontend.layout import CIRCUIT_INFO, TEAM_INFO

# ── Session cache ─────────────────────────────────────────────────────────────
_SESSION_CACHE: dict = {}
_CACHE_LOCK = threading.Lock()

def _get_session(year, gp, session_type):
    key = f"{year}|{gp}|{session_type}"
    with _CACHE_LOCK:
        if key not in _SESSION_CACHE:
            sess = fastf1.get_session(year, gp, session_type)
            sess.load(laps=True, telemetry=True, weather=False, messages=False)
            _SESSION_CACHE[key] = sess
        return _SESSION_CACHE[key]

# ── Palette ───────────────────────────────────────────────────────────────────
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

_T  = "rgba(0,0,0,0)"
_G  = "rgba(255,255,255,0.04)"
_TK = "rgba(255,255,255,0.35)"
_M  = "JetBrains Mono, monospace"

TYRE_COLORS = {
    "SOFT": "#FCA5A5", "MEDIUM": "#FDE68A", "HARD": "rgba(255,255,255,0.7)",
    "INTERMEDIATE": "#6EE7B7", "WET": "#93C5FD", "UNKNOWN": "rgba(255,255,255,0.3)",
}

# ── Plotly layout helpers ─────────────────────────────────────────────────────

def _base_layout(y_title="", x_title="Distance (m)"):
    return dict(
        paper_bgcolor=_T, plot_bgcolor=_T,
        margin=dict(l=56, r=20, t=16, b=48),
        font=dict(family=_M, color=_TK, size=11),
        xaxis=dict(
            title=dict(text=x_title, font=dict(size=11, color=_TK)),
            gridcolor=_G, linecolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=10, color=_TK), showgrid=True, zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=11, color=_TK)),
            gridcolor=_G, linecolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=10, color=_TK), showgrid=True, zeroline=False,
        ),
        legend=dict(bgcolor=_T, font=dict(size=11, color="rgba(255,255,255,0.55)"),
                    orientation="h", y=1.08, x=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0d0d14", bordercolor="rgba(255,255,255,0.15)",
                        font=dict(family=_M, size=12, color="#fff")),
    )

def _map_layout(height=None):
    lay = dict(
        paper_bgcolor=_T, plot_bgcolor=_T,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                   range=[-0.04, 1.04], fixedrange=True),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                   scaleanchor="x", scaleratio=1,
                   range=[-0.04, 1.04], fixedrange=True),
        font=dict(family=_M),
        dragmode=False,
    )
    if height:
        lay["height"] = height
    return lay

def _empty_fig(msg="Load a session first"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False,
                       font=dict(color="rgba(255,255,255,0.25)", size=14, family=_M))
    fig.update_layout(**_base_layout())
    return fig

def _empty_map(msg="Load a session first"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False,
                       font=dict(color="rgba(255,255,255,0.25)", size=14, family=_M))
    fig.update_layout(**_map_layout())
    return fig

def _fmt_lap(seconds):
    try:
        s = float(seconds)
        if np.isnan(s): return "—:——.———"
        m = int(s // 60)
        return f"{m}:{s % 60:06.3f}"
    except Exception:
        return "—:——.———"

def _fmt_sector(td):
    try: return f"{td.total_seconds():.3f}s"
    except Exception: return "—"

def _driver_options(drivers):
    return [{"label": d, "value": d, "title": TEAM_COLORS.get(d, "#888888")}
            for d in sorted(drivers)]

# ── Track map ─────────────────────────────────────────────────────────────────
def _build_track_map(session, driver):
    lap = session.laps.pick_drivers(driver).pick_fastest()
    pos = lap.get_pos_data().copy()
    car = lap.get_car_data().copy()

    pos["_t"] = pos["SessionTime"].dt.total_seconds()
    car["_t"] = car["SessionTime"].dt.total_seconds()
    pos = pos.sort_values("_t").reset_index(drop=True)
    car = car.sort_values("_t").reset_index(drop=True)

    merged = pd.merge_asof(
        pos[["_t", "X", "Y"]],
        car[["_t", "Speed"]],
        on="_t", direction="nearest",
    ).dropna(subset=["X", "Y", "Speed"])

    x   = merged["X"].values.astype(float)
    y   = merged["Y"].values.astype(float)
    spd = merged["Speed"].values.astype(float)

    mn_x, mx_x = x.min(), x.max()
    mn_y, mx_y = y.min(), y.max()
    rng = max(mx_x - mn_x, mx_y - mn_y) or 1.0
    nx  = (x - mn_x) / rng
    ny  = (y - mn_y) / rng

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=nx, y=ny, mode="lines",
                             line=dict(color="rgba(255,255,255,0.04)", width=20),
                             hoverinfo="none", showlegend=False))
    fig.add_trace(go.Scatter(x=nx, y=ny, mode="lines",
                             line=dict(color="rgba(255,255,255,0.10)", width=10),
                             hoverinfo="none", showlegend=False))
    fig.add_trace(go.Scatter(
        x=nx, y=ny, mode="markers",
        marker=dict(
            size=5, color=spd, colorscale="Plasma", showscale=True,
            cmin=float(np.percentile(spd, 5)), cmax=float(np.percentile(spd, 95)),
            colorbar=dict(
                title=dict(text="km/h", font=dict(size=11, family=_M, color=_TK)),
                tickfont=dict(size=10, family=_M, color=_TK),
                thickness=10, len=0.6,
                bgcolor=_T, bordercolor="rgba(255,255,255,0.08)",
            ),
        ),
        hovertemplate="Speed: %{marker.color:.0f} km/h<extra></extra>",
        showlegend=False,
    ))
    lay = _map_layout()
    lay["margin"] = dict(l=0, r=60, t=8, b=8)
    fig.update_layout(**lay)
    return fig

# ── Replay data builder (optimized: aggressive sampling + caching) ────────────
_REPLAY_CACHE = {}
_REPLAY_CACHE_LOCK = threading.Lock()

def _build_replay_data(session, max_frames: int = 200):
    """Build replay data with aggressive downsampling for fast, smooth animation.
    max_frames=200 keeps data small so the browser renders quickly.
    """
    cache_key = f"{session.event['EventName']}_{session.event['EventDate']}"
    with _REPLAY_CACHE_LOCK:
        if cache_key in _REPLAY_CACHE:
            return _REPLAY_CACHE[cache_key]

    SAMPLE = 16  # heavier downsampling for speed (was 8)
    try:
        fp = session.laps.pick_fastest().get_pos_data()
        raw_ox = fp["X"].values.astype(float)
        raw_oy = fp["Y"].values.astype(float)
    except Exception:
        raw_ox = raw_oy = np.array([])

    # Load position data - required for replay
    try:
        if not hasattr(session, 'pos_data') or session.pos_data is None or len(session.pos_data) == 0:
            session.load_pos_data()
    except Exception as e:
        print(f"Warning: Could not load pos_data: {e}")
        return None
    
    # Load car data for speed - optional, replay works without it
    try:
        if not hasattr(session, 'car_data') or session.car_data is None or len(session.car_data) == 0:
            session.load_car_data()
    except Exception:
        pass

    drivers = session.laps["Driver"].dropna().unique().tolist()
    drv_dfs: dict = {}
    drv_speeds: dict = {}

    driver_car_map = {}
    try:
        car_map = session.laps[["Driver", "DriverNumber"]].dropna().drop_duplicates("Driver")
        for drv, car in car_map.values:
            if drv and pd.notna(car):
                driver_car_map[drv] = str(int(car)) if not isinstance(car, str) else str(car)
    except Exception:
        driver_car_map = {}

    for drv in drivers:
        try:
            car_key = driver_car_map.get(drv, str(drv))
            if not session.pos_data or car_key not in session.pos_data:
                if session.pos_data:
                    car_key = next((k for k in session.pos_data if str(k) == str(car_key)), None)
                else:
                    continue
            if not car_key or not session.pos_data:
                continue
            pos_df = session.pos_data[car_key].copy()
            pos_df["_t"] = pos_df["SessionTime"].dt.total_seconds()
            pos_df = pos_df[["_t", "X", "Y"]].dropna()

            if hasattr(session, 'car_data') and session.car_data and car_key in session.car_data:
                try:
                    car_df = session.car_data[car_key].copy()
                    car_df["_t"] = car_df["SessionTime"].dt.total_seconds()
                    car_df = car_df[["_t", "Speed"]].dropna()
                    merged = pd.merge_asof(
                        pos_df.sort_values("_t"),
                        car_df.sort_values("_t"),
                        on="_t", direction="nearest"
                    )
                    drv_speeds[drv] = merged[["_t", "Speed"]].values
                except Exception:
                    pass

            pos_df = pos_df.iloc[::SAMPLE].reset_index(drop=True)
            if len(pos_df) > 5:
                drv_dfs[drv] = pos_df
        except Exception:
            pass

    if not drv_dfs:
        return None

    all_x = np.concatenate(
        ([raw_ox] if len(raw_ox) else []) +
        [df["X"].values.astype(float) for df in drv_dfs.values()]
    )
    all_y = np.concatenate(
        ([raw_oy] if len(raw_oy) else []) +
        [df["Y"].values.astype(float) for df in drv_dfs.values()]
    )
    mn_x, mx_x = float(all_x.min()), float(all_x.max())
    mn_y, mx_y = float(all_y.min()), float(all_y.max())
    rng = max(mx_x - mn_x, mx_y - mn_y) or 1.0

    def _nx(v): return round((float(v) - mn_x) / rng, 4)
    def _ny(v): return round((float(v) - mn_y) / rng, 4)

    track_nx = [_nx(v) for v in raw_ox] if len(raw_ox) else []
    track_ny = [_ny(v) for v in raw_oy] if len(raw_oy) else []

    spine = max(drv_dfs, key=lambda d: len(drv_dfs[d]))
    t_vals = drv_dfs[spine]["_t"].values
    stride = max(1, len(t_vals) // max_frames)
    t_axis = t_vals[::stride]

    drv_t = {d: df["_t"].values for d, df in drv_dfs.items()}

    frames = []
    for t in t_axis:
        fd = {}
        for drv, df in drv_dfs.items():
            idx = min(int(np.searchsorted(drv_t[drv], t)), len(df) - 1)
            row = df.iloc[idx]
            speed_val = 0
            if drv in drv_speeds and drv_speeds[drv] is not None:
                arr = drv_speeds[drv]
                if len(arr) > 0:
                    sidx = min(int(np.searchsorted(arr[:, 0], t)), len(arr) - 1)
                    speed_val = int(arr[sidx, 1])
            fd[drv] = {
                "x": _nx(row["X"]),
                "y": _ny(row["Y"]),
                "speed": speed_val,
            }
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
        "drivers":    list(drv_dfs.keys()),
        "colors":     {d: TEAM_COLORS.get(d, "#888888") for d in drv_dfs},
        "total_laps": total_laps,
    }
    with _REPLAY_CACHE_LOCK:
        _REPLAY_CACHE[cache_key] = result
    return result

def _replay_fig(data, frame_idx: int = 0):
    if not data or not data.get("frames"):
        return _empty_map("Load a session to see the race replay")
    tx = data["track_x"]
    ty = data["track_y"]
    drivers = data["drivers"]
    colors = data["colors"]
    idx = min(int(frame_idx), len(data["frames"]) - 1)
    frame = data["frames"][idx]
    dx = [frame["d"].get(d, {"x": 0.5})["x"] for d in drivers]
    dy = [frame["d"].get(d, {"y": 0.5})["y"] for d in drivers]
    dc = [colors.get(d, "#888888") for d in drivers]
    ds = [frame["d"].get(d, {}).get("speed", 0) for d in drivers]
    fig = go.Figure()
    if tx:
        fig.add_trace(go.Scatter(x=tx, y=ty, mode="lines",
                                 line=dict(color="rgba(232,0,45,0.06)", width=28),
                                 hoverinfo="none", showlegend=False))
        fig.add_trace(go.Scatter(x=tx, y=ty, mode="lines",
                                 line=dict(color="rgba(255,255,255,0.06)", width=16),
                                 hoverinfo="none", showlegend=False))
        fig.add_trace(go.Scatter(x=tx, y=ty, mode="lines",
                                 line=dict(color="rgba(255,255,255,0.22)", width=3),
                                 hoverinfo="none", showlegend=False))
    trail_len = min(6, idx)
    if trail_len > 1:
        for di, drv in enumerate(drivers):
            trail_x, trail_y = [], []
            for back in range(trail_len, 0, -1):
                fi = max(0, idx - back)
                f = data["frames"][fi]
                trail_x.append(f["d"].get(drv, {"x": dx[di]})["x"])
                trail_y.append(f["d"].get(drv, {"y": dy[di]})["y"])
            col = colors.get(drv, "#888888")
            hc = col.lstrip("#")
            r, g, b = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
            for ti in range(len(trail_x) - 1):
                alpha = (ti + 1) / trail_len * 0.35
                fig.add_trace(go.Scatter(
                    x=trail_x[ti:ti+2], y=trail_y[ti:ti+2], mode="lines",
                    line=dict(color=f"rgba({r},{g},{b},{alpha:.2f})", width=4 + ti * 0.5),
                    hoverinfo="none", showlegend=False,
                ))
    for di, drv in enumerate(drivers):
        col = colors.get(drv, "#888888")
        hc = col.lstrip("#")
        r, g, b = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
        fig.add_trace(go.Scatter(
            x=[dx[di]], y=[dy[di]], mode="markers",
            marker=dict(size=22, color=f"rgba({r},{g},{b},0.18)", line=dict(width=0)),
            hoverinfo="none", showlegend=False,
        ))
    fig.add_trace(go.Scatter(
        x=dx, y=dy, mode="markers+text",
        marker=dict(size=13, color=dc, line=dict(width=2, color="rgba(0,0,0,0.85)"), symbol="circle"),
        text=drivers, textposition="top center",
        textfont=dict(family=_M, size=9, color="rgba(255,255,255,0.85)"),
        customdata=[[d, s] for d, s in zip(drivers, ds)],
        hovertemplate="<b>%{text}</b><br>Speed: %{customdata[1]} km/h<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(**_map_layout())
    return fig

def _build_replay_leaderboard(data, frame_idx):
    if not data or not data.get("frames"):
        return [html.Div("Load a session", className="empty-state")]
    idx = min(int(frame_idx), len(data["frames"]) - 1)
    frame = data["frames"][idx]
    colors = data["colors"]
    drivers = data["drivers"]
    driver_speeds = [(d, frame["d"].get(d, {}).get("speed", 0)) for d in drivers]
    driver_speeds.sort(key=lambda x: -x[1])
    rows = []
    for pos, (drv, spd) in enumerate(driver_speeds, 1):
        color = colors.get(drv, "#888888")
        rows.append(html.Div(className="replay-lb-row", children=[
            html.Div(str(pos), className="replay-lb-pos"),
            html.Div(className="replay-lb-dot", style={"background": color, "boxShadow": f"0 0 8px {color}"}),
            html.Div(drv, className="replay-lb-drv"),
            html.Div(f"{spd} km/h" if spd else "—", className="replay-lb-speed"),
        ]))
    return rows

def _build_standings(session):
    try:
        laps = session.laps.copy()
        last = (laps.sort_values("LapNumber").groupby("Driver").last()
                    .reset_index().sort_values("Position").head(20))
        fl = laps["LapTime"].min()
        rows = []
        for i, row in enumerate(last.itertuples()):
            drv = row.Driver
            pos = int(row.Position) if not pd.isna(row.Position) else i + 1
            comp = str(getattr(row, "Compound", "H"))
            ci = comp[0] if comp and comp != "nan" else "H"
            dl = laps[laps["Driver"] == drv]
            best = dl["LapTime"].min()
            last_ = getattr(row, "LapTime", None)
            color = TEAM_COLORS.get(drv, "#888888")
            bs = _fmt_lap(best.total_seconds() if pd.notna(best) else None)
            ls = _fmt_lap(last_.total_seconds() if hasattr(last_, "total_seconds") else None)
            rows.append(html.Div(className="driver-row", children=[
                html.Span(str(pos), className="pos-num"),
                html.Span(drv, className="driver-tag", style={"borderLeft": f"3px solid {color}", "paddingLeft": "7px"}),
                html.Div(className="driver-info", children=[
                    html.Span(drv, className="driver-name", style={"color": color}),
                    html.Span(getattr(row, "Team", ""), className="team-name"),
                ]),
                html.Div(html.Span(ci, className=f"tyre-badge tyre-{ci}"), style={"textAlign": "right"}),
                html.Span("—", className="gap-val"),
                html.Span(ls, className="lap-time"),
                html.Span(bs, className=f"lap-time {'fastest' if best == fl else 'best'}"),
            ]))
        return rows or [html.Div("No lap data", className="empty-state")]
    except Exception as e:
        return [html.Div(f"Standings error: {e}", className="empty-state")]

# ═════════════════════════════════════════════════════════════════════════════
def register_callbacks(app):

    # ── Telemetry type store ──────────────────────────────────────────────────
    @app.callback(
        Output("store-tel-type", "data"),
        Input("btn-tel-speed", "n_clicks"),
        Input("btn-tel-throttle", "n_clicks"),
        Input("btn-tel-brake", "n_clicks"),
        Input("btn-tel-gear", "n_clicks"),
    )
    def update_tel_type(speed, throttle, brake, gear):
        if not ctx.triggered:
            return "speed"
        btn_id = ctx.triggered_id
        if btn_id == "btn-tel-speed":    return "speed"
        if btn_id == "btn-tel-throttle": return "throttle"
        if btn_id == "btn-tel-brake":    return "brake"
        if btn_id == "btn-tel-gear":     return "gear"
        return "speed"

    @app.callback(
        Output("btn-tel-speed",    "className"),
        Output("btn-tel-throttle", "className"),
        Output("btn-tel-brake",    "className"),
        Output("btn-tel-gear",     "className"),
        Input("store-tel-type", "data"),
    )
    def update_button_styles(selected):
        base = "outline-btn"
        active = "outline-btn active"
        return (active if selected == "speed" else base,
                active if selected == "throttle" else base,
                active if selected == "brake" else base,
                active if selected == "gear" else base)

    # ── Tab switching ─────────────────────────────────────────────────────────
    PANELS = ["panel-session", "panel-standings", "panel-track",
              "panel-telemetry", "panel-compare", "panel-analysis",
              "panel-circuits", "panel-teams", "panel-replay", "panel-calendar"]
    TABS = ["tab-session", "tab-standings", "tab-track",
            "tab-telemetry", "tab-compare", "tab-analysis",
            "tab-circuits", "tab-teams", "tab-replay", "tab-calendar"]

    @app.callback(
        [Output(p, "className") for p in PANELS] +
        [Output(t, "className") for t in TABS],
        [Input(t, "n_clicks") for t in TABS] +
        [Input("module-track-map", "n_clicks"),
         Input("module-telemetry", "n_clicks"),
         Input("module-compare", "n_clicks"),
         Input("module-replay", "n_clicks")],
        prevent_initial_call=False,
    )
    def switch_tab(*args):
        triggered = ctx.triggered_id or "tab-session"
        # Map module cards to tabs
        module_to_tab = {
            "module-track-map": "tab-track",
            "module-telemetry": "tab-telemetry",
            "module-compare": "tab-compare",
            "module-replay": "tab-replay"
        }
        if triggered in module_to_tab:
            triggered = module_to_tab[triggered]
        active = TABS.index(triggered) if triggered in TABS else 0
        panels = ["panel active" if i == active else "panel" for i in range(len(PANELS))]
        tabs = ["tab-btn active" if i == active else "tab-btn" for i in range(len(TABS))]
        return (*panels, *tabs)


    # ── Circuit details ────────────────────────────────────────────────────────
    @app.callback(
        Output("circuit-length", "children"),
        Output("circuit-corners", "children"),
        Output("circuit-firstgp", "children"),
        Output("circuit-races", "children"),
        Output("circuit-best-lap", "children"),
        Output("circuit-best-driver", "children"),
        Output("circuit-lap-record", "children"),
        Output("circuit-record-holder", "children"),
        Output("circuit-description", "children"),
        Input("sel-circuit", "value"),
        Input("store-session", "data"),
    )
    def update_circuit_details(circuit_key, store):
        circuit = CIRCUIT_INFO.get(circuit_key, {})
        length = circuit.get("length", "—")
        corners = circuit.get("corners", "—")
        first_gp = circuit.get("first_gp", "—")
        races = circuit.get("races", "—")
        lap_record = circuit.get("lap_record", "—")
        record_holder = circuit.get("record_holder", "—")
        description = circuit.get("description", "Select a circuit to see details.")
        best_lap = best_driver = "—"
        if store and store.get("gp") == circuit_key:
            try:
                session = _get_session(store["year"], store["gp"], store["session_type"])
                fastest = session.laps.pick_fastest()
                if fastest is not None:
                    best_lap = str(fastest["LapTime"])
                    best_driver = fastest["Driver"]
            except Exception:
                pass
        return length, corners, first_gp, races, best_lap, best_driver, lap_record, record_holder, description

    # ── Team panel ─────────────────────────────────────────────────────────────
    @app.callback(
        Output("team-name", "children"),
        Output("team-drivers", "children"),
        Output("team-desc", "children"),
        Output("team-color-band", "style"),
        Output("team-lineup", "children"),
        Output("team-championships", "children"),
        Output("team-championships-sub", "children"),
        Output("team-drivers-championships", "children"),
        Output("team-drivers-championships-sub", "children"),
        Output("team-wins", "children"),
        Output("team-wins-sub", "children"),
        Output("team-poles", "children"),
        Output("team-poles-sub", "children"),
        Output("team-founded", "children"),
        Output("team-founded-sub", "children"),
        Output("team-base", "children"),
        Output("team-base-sub", "children"),
        Input("sel-team", "value"),
    )
    def update_team_panel(team_name):
        team = TEAM_INFO.get(team_name, {})
        color = team.get("color", "rgba(255,255,255,0.12)")
        drivers = team.get("drivers", [])
        driver_tags = [html.Span(d, className="team-badge",
                                 style={"background": TEAM_COLORS.get(d, "rgba(255,255,255,0.15)"),
                                        "color": "#fff"}) for d in drivers]
        lineup = html.Div(driver_tags, className="team-badges")
        return (team_name, lineup, team.get("description", "Select a team to view stats."),
                {"background": color, "height": "12px", "borderRadius": "6px", "boxShadow": f"0 0 14px {color}"},
                lineup, team.get("championships", "—"), "titles",
                team.get("drivers_championships", "—"), "titles",
                team.get("wins", "—"), "wins", team.get("poles", "—"), "poles",
                team.get("founded", "—"), "year", team.get("base", "—"), "location")

    # ── Session load ──────────────────────────────────────────────────────────
    @app.callback(
        Output("store-session", "data"),
        Output("session-type-label", "children"),
        Output("gp-title-label", "children"),
        Output("lap-display", "children"),
        Output("weather-air", "children"),
        Output("weather-track", "children"),
        Output("weather-wind", "children"),
        Output("stat-best", "children"),
        Output("stat-best-drv", "children"),
        Output("stat-avg", "children"),
        Output("stat-avg-sub", "children"),
        Output("stat-cons", "children"),
        Output("stat-cons-sub", "children"),
        Output("stat-worst", "children"),
        Output("stat-worst-sub", "children"),
        Output("status-dot", "className"),
        Output("status-text", "children"),
        Output("standings-body", "children"),
        Output("plot-btns", "className"),
        Output("total-laps-stat", "children"),
        Output("fastest-stat", "children"),
        Output("fastest-drv-stat", "children"),
        Output("sel-driver1", "options"),
        Output("sel-driver1", "value"),
        Output("sel-driver2", "options"),
        Output("sel-driver2", "value"),
        Output("sel-tel-driver", "options"),
        Output("sel-tel-driver", "value"),
        Output("circuit-name", "children"),
        Output("circuit-len", "children"),
        Input("load-btn", "n_clicks"),
        State("sel-year", "value"), State("sel-gp", "value"),
        State("sel-session", "value"),
        prevent_initial_call=True,
    )
    def load_session_cb(_, year, gp, session_type):
        def _err(msg):
            return (None, session_type or "?", msg, "—/—", "— AIR", "— TRK", "— m/s",
                    "—", "—", "—", "—", "—", "—", "—", "—",
                    "status-dot idle", f"ERROR — {msg}", [html.Div(msg, className="empty-state")],
                    "btn-row disabled-plots", "—", "—", "—",
                    [], "VER", [], "HAM", [], None, "—", "—")
        try:
            session = _get_session(year, gp, session_type)
        except Exception as e:
            return _err(str(e))

        try:
            wx = session.weather_data
            air = f"{wx['AirTemp'].mean():.0f}\u00b0 AIR" if not wx.empty else "— AIR"
            track_w = f"{wx['TrackTemp'].mean():.0f}\u00b0 TRK" if not wx.empty else "— TRK"
            wind = f"{wx['WindSpeed'].mean():.1f} m/s" if not wx.empty else "— m/s"
        except Exception:
            air = track_w = wind = "—"

        actual = sorted(session.laps["Driver"].dropna().unique().tolist())
        opts = _driver_options(actual)
        d1 = actual[0] if len(actual) > 0 else "VER"
        d2 = actual[1] if len(actual) > 1 else actual[0] if len(actual) > 0 else "HAM"

        try:
            stats = lap_time_analysis(session, d1)
            best = _fmt_lap(stats["best_lap"])
            avg = _fmt_lap(stats["average_lap"])
            cons = f"{stats['consistency_std']:.3f}s"
            worst = _fmt_lap(stats["worst_lap"])
        except Exception:
            best = avg = cons = worst = "—"

        try:
            total_laps = str(int(session.laps["LapNumber"].max()))
        except Exception:
            total_laps = "—"
        try:
            fl = session.laps.pick_fastest()
            fl_time = _fmt_lap(fl["LapTime"].total_seconds())
            fl_drv = str(fl["Driver"])
        except Exception:
            fl_time = fl_drv = "—"

        standings = _build_standings(session)
        gp_label = gp.replace("_", " ").title() + " Grand Prix"
        store = dict(year=year, gp=gp, session_type=session_type, driver1=d1, driver2=d2)
        circuit_name = CIRCUIT_INFO.get(gp, {}).get("name", gp_label)
        circuit_len = CIRCUIT_INFO.get(gp, {}).get("length", "—")

        return (store, f"{session_type} \u00b7 {year}", gp_label, f"{total_laps}/{total_laps}",
                air, track_w, wind, best, d1, avg, "driver avg", cons, "std dev (s)", worst, "driver",
                "status-dot ready", f"SESSION READY — {year} {gp_label} {session_type}",
                standings, "btn-row", total_laps, fl_time, fl_drv,
                opts, d1, opts, d2, opts, d1, circuit_name, circuit_len)

    @app.callback(
        Output("track-map-graph", "figure"),
        Input("store-session", "data"),
        prevent_initial_call=True,
    )
    def update_track_map(store):
        if not store: return _empty_map("Load a session first")
        try:
            sess = _get_session(store["year"], store["gp"], store["session_type"])
            return _build_track_map(sess, store["driver1"])
        except Exception as e:
            return _empty_map(f"Track map error: {e}")

    @app.callback(
        Output("tel-graph", "figure"),
        Output("tel-chart-title", "children"),
        Input("store-session", "data"),
        Input("sel-tel-driver", "value"),
        Input("btn-tel-speed", "n_clicks"),
        Input("btn-tel-throttle", "n_clicks"),
        Input("btn-tel-brake", "n_clicks"),
        Input("btn-tel-gear", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_telemetry(store, tel_driver, sp, th, br, ge):
        if not store: return _empty_fig("Load a session first"), "—"
        driver = tel_driver or store.get("driver1", "VER")
        cmap = {
            "btn-tel-speed": ("Speed", "Speed (km/h)", "#E8002D"),
            "btn-tel-throttle": ("Throttle", "Throttle (%)", "#34D399"),
            "btn-tel-brake": ("Brake", "Brake", "#EF4444"),
            "btn-tel-gear": ("nGear", "Gear", "#F59E0B"),
        }
        ch, yl, col = cmap.get(ctx.triggered_id, ("Speed", "Speed (km/h)", "#E8002D"))
        try:
            sess = _get_session(store["year"], store["gp"], store["session_type"])
            lap = sess.laps.pick_drivers(driver).pick_fastest()
            tel = lap.get_car_data().add_distance()
            fig = go.Figure()
            def hex_to_rgba(hex_col, alpha=0.15):
                hc = hex_col.lstrip('#')
                r, g, b = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
                return f"rgba({r},{g},{b},{alpha})"
            fig.add_trace(go.Scatter(x=tel["Distance"], y=tel[ch], mode="lines",
                                     line=dict(color=col, width=2),
                                     fill="tozeroy", fillcolor=hex_to_rgba(col),
                                     name=driver, hovertemplate=f"%{{y:.1f}}<extra>{driver}</extra>"))
            fig.update_layout(**_base_layout(y_title=yl))
            return fig, f"{yl} — {driver}"
        except Exception as e:
            return _empty_fig(str(e)), f"Error: {e}"

    @app.callback(
        Output("cmp-graph", "figure"),
        Output("cmp-d1-name", "children"), Output("cmp-d2-name", "children"),
        Output("cmp-d1-lap", "children"), Output("cmp-d2-lap", "children"),
        Output("cmp-d1-s1", "children"), Output("cmp-d1-s2", "children"),
        Output("cmp-d1-s3", "children"), Output("cmp-d2-s1", "children"),
        Output("cmp-d2-s2", "children"), Output("cmp-d2-s3", "children"),
        Output("cmp-d1-dot", "style"), Output("cmp-d2-dot", "style"),
        Input("store-session", "data"),
        Input("sel-driver1", "value"),
        Input("sel-driver2", "value"),
        prevent_initial_call=True,
    )
    def update_compare(store, driver1, driver2):
        blank = ("—:——.———",) * 2 + ("—",) * 6
        default_dot = {"width": "12px", "height": "12px", "borderRadius": "50%",
                       "background": "rgba(255,255,255,0.18)", "flexShrink": "0"}
        if not store:
            return (_empty_fig(), "—", "—", *blank, default_dot, default_dot)
        try:
            sess = _get_session(store["year"], store["gp"], store["session_type"])
            d1 = driver1 or store.get("driver1", "VER")
            d2 = driver2 or store.get("driver2", "HAM")
            c1 = TEAM_COLORS.get(d1, "#E8002D")
            c2 = TEAM_COLORS.get(d2, "#3671C6")
            tel1, tel2, lap1, lap2 = compare_drivers(sess, d1, d2)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tel1["Distance"], y=tel1["Speed"], mode="lines",
                                     line=dict(color=c1, width=2), name=d1))
            fig.add_trace(go.Scatter(x=tel2["Distance"], y=tel2["Speed"], mode="lines",
                                     line=dict(color=c2, width=2, dash="dot"), name=d2))
            fig.update_layout(**_base_layout(y_title="Speed (km/h)"))
            d1l = _fmt_lap(lap1["LapTime"].total_seconds() if pd.notna(lap1["LapTime"]) else None)
            d2l = _fmt_lap(lap2["LapTime"].total_seconds() if pd.notna(lap2["LapTime"]) else None)
            d1s = [_fmt_sector(lap1.get(f"Sector{i}Time")) for i in [1,2,3]]
            d2s = [_fmt_sector(lap2.get(f"Sector{i}Time")) for i in [1,2,3]]
            dot1 = {"width": "12px", "height": "12px", "borderRadius": "50%",
                    "background": c1, "flexShrink": "0", "boxShadow": f"0 0 10px {c1}"}
            dot2 = {"width": "12px", "height": "12px", "borderRadius": "50%",
                    "background": c2, "flexShrink": "0", "boxShadow": f"0 0 10px {c2}"}
            return (fig, d1, d2, d1l, d2l, *d1s, *d2s, dot1, dot2)
        except Exception as e:
            return (_empty_fig(str(e)), "—", "—", *blank, default_dot, default_dot)

    # ── Replay store (lazy load) ─────────────────────────────────────────────
    @app.callback(
        Output("store-replay-data", "data"),
        Output("replay-legend", "children"),
        Output("replay-frame-slider", "max"),
        Output("replay-lap-total", "children"),
        Input("store-session", "data"),
        prevent_initial_call=True,
    )
    def build_replay_store(store):
        if not store: return None, [], 100, ""
        try:
            session = _get_session(store["year"], store["gp"], store["session_type"])
            data = _build_replay_data(session)
            if not data:
                return None, [html.Div("Replay: Position data unavailable for this session", className="empty-state")], 100, ""
            legend = [html.Div(className="replay-legend-chip", children=[
                html.Div(className="replay-legend-chip-dot",
                         style={"background": data["colors"].get(d, "#888"), "boxShadow": f'0 0 6px {data["colors"].get(d, "#888")}'}),
                html.Span(d, className="replay-legend-chip-label"),
            ]) for d in data["drivers"]]
            return data, legend, max(0, data["total"] - 1), f"/ {data['total_laps']}"
        except Exception as e:
            return None, [html.Div(f"Replay error: {str(e)[:80]}", className="empty-state")], 100, ""

    @app.callback(
        Output("replay-graph", "figure"),
        Output("replay-lap-num", "children"),
        Output("replay-time-val", "children"),
        Output("replay-leaderboard-body", "children"),
        Input("store-replay-data", "data"),
        Input("replay-frame-slider", "value"),
        prevent_initial_call=True,
    )
    def render_replay_frame(data, frame_idx):
        if not data: return _empty_map("Load a session to see the race replay"), "—", "—:—:—", []
        try:
            idx = int(frame_idx or 0)
            total = max(1, int(data.get("total", 1)))
            laps = int(data.get("total_laps", 1))
            frames = data.get("frames", [])
            if not frames or idx >= len(frames):
                return _empty_map("No replay data available"), "—", "—:—:—", []
            lap_now = max(1, min(laps, int(idx / total * laps) + 1)) if laps else 1
            frame_pos = min(idx, len(frames) - 1)
            if frame_pos < 0 or frame_pos >= len(frames):
                return _empty_map("Invalid frame index"), "—", "—:—:—", []
            t_sec = float(frames[frame_pos].get("t", 0)) if frame_pos < len(frames) else 0
            m = int(t_sec // 60)
            s = int(t_sec % 60)
            cs = int((t_sec % 1) * 100)
            t_fmt = f"{m:02d}:{s:02d}.{cs:02d}"
            leaderboard = _build_replay_leaderboard(data, idx)
            return _replay_fig(data, idx), str(lap_now), t_fmt, leaderboard
        except Exception as e:
            return _empty_map(f"Replay error: {str(e)[:50]}"), "—", "—:—:—", []

    @app.callback(
        Output("replay-interval", "disabled"),
        Output("store-replay-playing", "data"),
        Output("replay-play-btn", "children"),
        Input("replay-play-btn", "n_clicks"),
        Input("replay-reset-btn", "n_clicks"),
        Input("store-session", "data"),
        State("store-replay-playing", "data"),
        prevent_initial_call=True,
    )
    def toggle_replay(play_clicks, reset_clicks, store_session, is_playing):
        triggered = ctx.triggered_id
        if triggered == "replay-reset-btn":
            return True, False, "\u25b6  PLAY"
        if triggered == "store-session":
            if not store_session:
                return True, False, "\u25b6  PLAY"
            return False, True, "\u23f8  PAUSE"
        new_playing = not bool(is_playing)
        return (not new_playing), new_playing, ("\u23f8  PAUSE" if new_playing else "\u25b6  PLAY")

    @app.callback(
        Output("replay-frame-slider", "value"),
        Input("replay-interval", "n_intervals"),
        Input("replay-reset-btn", "n_clicks"),
        Input("store-session", "data"),
        State("replay-frame-slider", "value"),
        State("replay-frame-slider", "max"),
        State("store-replay-playing", "data"),
        prevent_initial_call=True,
    )
    def advance_frame(n_intervals, reset_clicks, store_session, current, max_val, is_playing):
        triggered = ctx.triggered_id
        if triggered in ("replay-reset-btn", "store-session"):
            return 0
        if not is_playing:
            return no_update
        # Jump 4 frames per tick for fast, smooth animation (50ms * 4 = 200ms per frame)
        current_val = int(current or 0)
        max_val_int = int(max_val or 100)
        nxt = current_val + 4
        if nxt >= max_val_int:
            return 0  # Loop back to start
        return nxt

    # ── Quick-plot buttons ─────────────────────────────────────────────────
    @app.callback(
        Output("tab-telemetry", "n_clicks"),
        Output("tab-track", "n_clicks"),
        Input("btn-speed-trace", "n_clicks"),
        Input("btn-tel-panel", "n_clicks"),
        Input("btn-lap-times", "n_clicks"),
        Input("btn-compounds", "n_clicks"),
        Input("btn-track-map", "n_clicks"),
        State("tab-telemetry", "n_clicks"),
        State("tab-track", "n_clicks"),
        prevent_initial_call=True,
    )
    def quick_plot_buttons(speed_clicks, tel_clicks, lap_clicks, compound_clicks,
                           track_clicks, tel_state, track_state):
        tid = ctx.triggered_id
        if tid in ["btn-speed-trace", "btn-tel-panel", "btn-lap-times", "btn-compounds"]:
            return (tel_state or 0) + 1, track_state or 0
        elif tid == "btn-track-map":
            return tel_state or 0, (track_state or 0) + 1
        return no_update, no_update

    @app.callback(
        Output("sel-gp", "value"),
        Output("sel-year", "value"),
        Output("tab-session", "n_clicks"),
        Input({"type": "calendar-race-card", "round": ALL}, "n_clicks"),
        State("sel-year", "value"),
        prevent_initial_call=True,
    )
    def calendar_card_click(n_clicks_list, current_year):
        from src.frontend.layout import F1_CALENDAR_2025
        if not any(n_clicks_list):
            return no_update, no_update, no_update
        triggered = ctx.triggered_id
        if not triggered or triggered.get("type") != "calendar-race-card":
            return no_update, no_update, no_update
        round_num = triggered["round"]
        race = next((r for r in F1_CALENDAR_2025 if r["round"] == round_num), None)
        if not race:
            return no_update, no_update, no_update
        return race["key"], 2025, 1

    @app.callback(
        Output("calendar-hero-title", "children"),
        Output("calendar-upcoming-label", "children"),
        Output("calendar-upcoming-grid", "children"),
        Output("calendar-completed-label", "children"),
        Output("calendar-completed-grid", "children"),
        Input("sel-calendar-year", "value"),
    )
    def update_calendar(selected_year):
        from src.frontend.layout import F1_CALENDAR_2025
        from datetime import datetime, date, timedelta
        if selected_year != 2025:
            return (f"{selected_year} SEASON",
                   [html.Div("No calendar data available for this year", className="empty-state")],
                   [], None, [])
        calendar_data = F1_CALENDAR_2025
        today = date.today()
        past = []
        upcoming = []
        def _race_card(race, rd, is_current):
            extra_cls = " current-week" if is_current else ""
            if rd < today and not is_current:
                extra_cls = " past"
            color = "#E8002D" if is_current else "rgba(255,255,255,0.08)"
            return html.Div(className=f"race-card{extra_cls}", style={"--race-color": color},
                            id={"type": "calendar-race-card", "round": race["round"]}, n_clicks=0,
                            children=[html.Div(f"ROUND {race['round']:02d}", className="race-round"),
                                      html.Div(race["name"], className="race-name"),
                                      html.Div(race["circuit"], className="race-circuit"),
                                      html.Div(className="race-date-row", children=[
                                          html.Span(rd.strftime("%d %b %Y"), className="race-date"),
                                          html.Span(race["country"], className="race-country-flag"),
                                      ])])
        for race in calendar_data:
            rd = datetime.strptime(race["date"], "%Y-%m-%d").date()
            race_week_start = rd
            race_week_end = rd
            is_current = race_week_start <= today <= race_week_end + timedelta(days=2)
            if rd < today and not is_current:
                past.append((race, rd, False))
            else:
                upcoming.append((race, rd, is_current))
        upcoming_cards = [_race_card(r, d, c) for r, d, c in upcoming]
        past_cards = [_race_card(r, d, c) for r, d, c in reversed(past)]
        upcoming_label = [html.Div("UPCOMING", className="section-text"), html.Span()]
        past_label = [html.Div("COMPLETED", className="section-text"), html.Span()]
        return (f"{selected_year} SEASON", upcoming_label if upcoming else None,
                upcoming_cards, past_label if past else None, past_cards)
