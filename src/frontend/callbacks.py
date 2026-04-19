# -*- coding: utf-8 -*-
"""callbacks.py - v3 complete fix
ROOT CAUSES FIXED:
  1. TRACK MAP BLANK  - merge_channels after add_distance() fails silently.
                        Fix: merge pos + car data on SessionTime float seconds.
  2. TELEMETRY BLANK  - only fired on button click, never on session load.
                        Fix: add store-session as an Input trigger.
  3. REPLAY BROKEN    - session.pos_data[drv] doesn't exist on older FastF1.
                        Fix: use session.pos_data[drv] with correct column access
                        (FastF1 >= 3.x stores it as a dict attr after telemetry load).
  4. SPEED            — load ONCE into process cache with threading.Lock.
  5. 2026 added       — layout.py handles this; callbacks just use whatever year passed.
"""

from dash import Input, Output, State, ctx, no_update
from dash import html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os, threading

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
            sess.load(telemetry=True, laps=True, weather=True, messages=False)
            _SESSION_CACHE[key] = sess
        return _SESSION_CACHE[key]


# ── Team colours ──────────────────────────────────────────────────────────────
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
_G  = "rgba(255,255,255,0.05)"
_TK = "rgba(255,255,255,0.3)"
_M  = "DM Mono, monospace"


# ── Layout helpers ────────────────────────────────────────────────────────────
def _base_layout(y_title="", x_title="Distance (m)"):
    return dict(
        paper_bgcolor=_T, plot_bgcolor=_T,
        margin=dict(l=50, r=16, t=12, b=40),
        font=dict(family=_M, color=_TK, size=10),
        xaxis=dict(
            title=dict(text=x_title, font=dict(size=10, color=_TK)),
            gridcolor=_G, linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=9, color=_TK), showgrid=True, zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=10, color=_TK)),
            gridcolor=_G, linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=9, color=_TK), showgrid=True, zeroline=False,
        ),
        legend=dict(bgcolor=_T, font=dict(size=10, color="rgba(255,255,255,0.5)")),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a1a1e", bordercolor="rgba(255,255,255,0.15)",
                        font=dict(family=_M, size=11, color="#fff")),
    )


def _map_layout():
    return dict(
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


def _empty_fig(msg="Load a session first"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False,
                       font=dict(color="rgba(255,255,255,0.3)", size=13, family=_M))
    fig.update_layout(**_base_layout())
    return fig


def _empty_map(msg="Load a session first"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False,
                       font=dict(color="rgba(255,255,255,0.3)", size=13, family=_M))
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

    # Convert timedelta SessionTime to float seconds
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

    # Normalise
    mn_x, mx_x = x.min(), x.max()
    mn_y, mx_y = y.min(), y.max()
    rng = max(mx_x - mn_x, mx_y - mn_y) or 1.0
    nx  = (x - mn_x) / rng
    ny  = (y - mn_y) / rng

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=nx, y=ny, mode="lines",
                             line=dict(color="rgba(255,255,255,0.07)", width=12),
                             hoverinfo="none", showlegend=False))
    fig.add_trace(go.Scatter(
        x=nx, y=ny, mode="markers",
        marker=dict(
            size=4, color=spd, colorscale="Plasma", showscale=True,
            cmin=float(np.percentile(spd, 5)), cmax=float(np.percentile(spd, 95)),
            colorbar=dict(
                title=dict(text="km/h", font=dict(size=10, family=_M, color=_TK)),
                tickfont=dict(size=9, family=_M, color=_TK),
                thickness=10, len=0.7,
                bgcolor=_T, bordercolor="rgba(255,255,255,0.08)",
            ),
        ),
        hovertemplate="Speed: %{marker.color:.0f} km/h<extra></extra>",
        showlegend=False,
    ))
    lay = _map_layout()
    lay["margin"] = dict(l=0, r=55, t=8, b=8)
    fig.update_layout(**lay)
    return fig


# ── Replay ────────────────────────────────────────────────────────────────────
def _build_replay_data(session, max_frames: int = 500):
    SAMPLE = 10

    # Track outline
    try:
        fp = session.laps.pick_fastest().get_pos_data()
        raw_ox = fp["X"].values.astype(float)
        raw_oy = fp["Y"].values.astype(float)
    except Exception:
        raw_ox = raw_oy = np.array([])

    drivers   = session.laps["Driver"].dropna().unique().tolist()
    drv_dfs: dict = {}

    # FastF1 pos_data is keyed by driver number / car number rather than driver code.
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
            if car_key not in session.pos_data:
                car_key = next((k for k in session.pos_data if str(k) == str(car_key)), None)
            if not car_key:
                continue
            df = session.pos_data[car_key].copy()
            df["_t"] = df["SessionTime"].dt.total_seconds()
            df = df[["_t", "X", "Y"]].dropna()
            df = df.iloc[::SAMPLE].reset_index(drop=True)
            if len(df) > 5:
                drv_dfs[drv] = df
        except Exception:
            pass

    if not drv_dfs:
        return None

    # Normalise globally
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

    # Build a track outline if fastest lap data is unavailable.
    if len(raw_ox) == 0 and len(drv_dfs):
        raw_ox = np.concatenate([df["X"].values.astype(float) for df in drv_dfs.values()])
        raw_oy = np.concatenate([df["Y"].values.astype(float) for df in drv_dfs.values()])

    # Time spine
    spine  = max(drv_dfs, key=lambda d: len(drv_dfs[d]))
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
            fd[drv] = [_nx(row["X"]), _ny(row["Y"])]
        frames.append({"t": round(float(t), 1), "d": fd})

    try:
        total_laps = int(session.laps["LapNumber"].max())
    except Exception:
        total_laps = 0

    return {
        "track_x":    track_nx,
        "track_y":    track_ny,
        "frames":     frames,
        "total":      len(frames),
        "drivers":    list(drv_dfs.keys()),
        "colors":     {d: TEAM_COLORS.get(d, "#888888") for d in drv_dfs},
        "total_laps": total_laps,
    }


def _replay_fig(data, frame_idx: int = 0):
    if not data or not data.get("frames"):
        return _empty_map("Load a session to see the race replay")

    tx      = data["track_x"]
    ty      = data["track_y"]
    drivers = data["drivers"]
    colors  = data["colors"]
    idx     = min(int(frame_idx), len(data["frames"]) - 1)
    frame   = data["frames"][idx]

    dx = [frame["d"].get(d, [0.5, 0.5])[0] for d in drivers]
    dy = [frame["d"].get(d, [0.5, 0.5])[1] for d in drivers]
    dc = [colors.get(d, "#888888") for d in drivers]

    fig = go.Figure()
    if tx:
        fig.add_trace(go.Scatter(x=tx, y=ty, mode="lines",
                                 line=dict(color="rgba(255,255,255,0.08)", width=14),
                                 hoverinfo="none", showlegend=False))
        fig.add_trace(go.Scatter(x=tx, y=ty, mode="lines",
                                 line=dict(color="rgba(255,255,255,0.22)", width=2),
                                 hoverinfo="none", showlegend=False))
    fig.add_trace(go.Scatter(
        x=dx, y=dy, mode="markers+text",
        marker=dict(size=14, color=dc,
                    line=dict(width=2, color="rgba(0,0,0,0.8)")),
        text=drivers,
        textposition="top center",
        textfont=dict(family=_M, size=8, color="rgba(255,255,255,0.8)"),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(**_map_layout())
    return fig


# ═════════════════════════════════════════════════════════════════════════════
def register_callbacks(app):

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

        if btn_id == "btn-tel-speed":
            return "speed"
        elif btn_id == "btn-tel-throttle":
            return "throttle"
        elif btn_id == "btn-tel-brake":
            return "brake"
        elif btn_id == "btn-tel-gear":
            return "gear"

        return "speed"


    @app.callback(
        Output("btn-tel-speed", "className"),
        Output("btn-tel-throttle", "className"),
        Output("btn-tel-brake", "className"),
        Output("btn-tel-gear", "className"),
        Input("store-tel-type", "data"),
    )
    def update_button_styles(selected):
        base = "outline-btn"
        active = "outline-btn active"

        return (
            active if selected == "speed" else base,
            active if selected == "throttle" else base,
            active if selected == "brake" else base,
            active if selected == "gear" else base,
        )
    # ── Tab switching ─────────────────────────────────────────────────────────
    @app.callback(
        Output("panel-session",   "className"),
        Output("panel-standings", "className"),
        Output("panel-track",     "className"),
        Output("panel-telemetry", "className"),
        Output("panel-compare",   "className"),
        Output("panel-circuits",  "className"),
        Output("panel-teams",     "className"),
        Output("panel-replay",    "className"),
        Output("tab-session",     "className"),
        Output("tab-standings",   "className"),
        Output("tab-track",       "className"),
        Output("tab-telemetry",   "className"),
        Output("tab-compare",     "className"),
        Output("tab-circuits",    "className"),
        Output("tab-teams",       "className"),
        Output("tab-replay",      "className"),
        Input("tab-session",   "n_clicks"), Input("tab-standings", "n_clicks"),
        Input("tab-track",     "n_clicks"), Input("tab-telemetry", "n_clicks"),
        Input("tab-compare",   "n_clicks"), Input("tab-circuits",   "n_clicks"),
        Input("tab-teams",     "n_clicks"), Input("tab-replay",    "n_clicks"),
        prevent_initial_call=False,
    )
    def switch_tab(*_):
        ORDER = ["tab-session", "tab-standings", "tab-track",
                 "tab-telemetry", "tab-compare", "tab-circuits",
                 "tab-teams", "tab-replay"]
        triggered = ctx.triggered_id or "tab-session"
        active    = ORDER.index(triggered) if triggered in ORDER else 0
        panels    = ["panel active" if i == active else "panel" for i in range(8)]
        tabs      = ["tab-btn active" if i == active else "tab-btn" for i in range(8)]
        return (*panels, *tabs)

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
        description = circuit.get("description", "Select a circuit to see more details.")
        best_lap = "—"
        best_driver = "—"

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
                                        "color": "#fff"})
                       for d in drivers]
        lineup = html.Div(driver_tags, className="team-badges")
        return (
            team_name,
            lineup,
            team.get("description", "Select a team to view its drivers and key stats."),
            {"background": color, "height": "10px", "borderRadius": "6px"},
            lineup,
            team.get("championships", "—"),
            "titles",
            team.get("drivers_championships", "—"),
            "titles",
            team.get("wins", "—"),
            "wins",
            team.get("poles", "—"),
            "poles",
            team.get("founded", "—"),
            "year",
            team.get("base", "—"),
            "location",
        )

    # ── Session load ──────────────────────────────────────────────────────────
    @app.callback(
        Output("store-session",      "data"),
        Output("session-type-label", "children"),
        Output("gp-title-label",     "children"),
        Output("lap-display",        "children"),
        Output("weather-air",        "children"),
        Output("weather-track",      "children"),
        Output("weather-wind",       "children"),
        Output("stat-best",          "children"),
        Output("stat-best-drv",      "children"),
        Output("stat-avg",           "children"),
        Output("stat-avg-sub",       "children"),
        Output("stat-cons",          "children"),
        Output("stat-cons-sub",      "children"),
        Output("stat-worst",         "children"),
        Output("stat-worst-sub",     "children"),
        Output("status-dot",         "className"),
        Output("status-text",        "children"),
        Output("standings-body",     "children"),
        Output("plot-btns",          "className"),
        Output("total-laps-stat",    "children"),
        Output("fastest-stat",       "children"),
        Output("fastest-drv-stat",   "children"),
        Output("sel-driver1",        "options"),
        Output("sel-driver1",        "value"),
        Output("sel-driver2",        "options"),
        Output("sel-driver2",        "value"),
        Output("sel-tel-driver",     "options"),
        Output("sel-tel-driver",     "value"),
        Output("circuit-name",       "children"),
        Output("circuit-len",        "children"),
        Input("load-btn", "n_clicks"),
        State("sel-year",    "value"), State("sel-gp",      "value"),
        State("sel-session", "value"), State("sel-driver1", "value"),
        State("sel-driver2", "value"),
        prevent_initial_call=True,
    )
    def load_session_cb(_, year, gp, session_type, driver1, driver2):
        def _err(msg):
            return (None, session_type or "?", msg, "—/—",
                    "— AIR", "— TRK", "— m/s",
                    "—", "—", "—", "—", "—", "—", "—", "—",
                    "status-dot idle", f"ERROR — {msg}",
                    [html.Div(msg, className="empty-state")],
                    "btn-row disabled-plots", "—", "—", "—",
                    [], driver1 or "—", [], driver2 or "—", [], None,
                    "—", "—")

        try:
            session = _get_session(year, gp, session_type)
        except Exception as e:
            return _err(str(e))

        try:
            wx = session.weather_data
            air     = f"{wx['AirTemp'].mean():.0f}° AIR"
            track_w = f"{wx['TrackTemp'].mean():.0f}° TRK"
            wind    = f"{wx['WindSpeed'].mean():.1f} m/s"
        except Exception:
            air = track_w = wind = "—"

        actual = sorted(session.laps["Driver"].dropna().unique().tolist())
        opts   = _driver_options(actual)
        d1     = driver1 if driver1 in actual else actual[0]
        d2     = driver2 if driver2 in actual else (actual[1] if len(actual) > 1 else actual[0])

        try:
            stats = lap_time_analysis(session, d1)
            best  = _fmt_lap(stats["best_lap"])
            avg   = _fmt_lap(stats["average_lap"])
            cons  = f"{stats['consistency_std']:.3f}s"
            worst = _fmt_lap(stats["worst_lap"])
        except Exception:
            best = avg = cons = worst = "—"

        try:
            total_laps = str(int(session.laps["LapNumber"].max()))
        except Exception:
            total_laps = "—"
        try:
            fl      = session.laps.pick_fastest()
            fl_time = _fmt_lap(fl["LapTime"].total_seconds())
            fl_drv  = str(fl["Driver"])
        except Exception:
            fl_time = fl_drv = "—"

        standings = _build_standings(session)
        gp_label  = gp.replace("_", " ").title() + " Grand Prix"
        store = dict(year=year, gp=gp, session_type=session_type, driver1=d1, driver2=d2)

        circuit_name = CIRCUIT_INFO.get(gp, {}).get("name", gp_label)
        circuit_len = CIRCUIT_INFO.get(gp, {}).get("length", "—")
        return (
            store,
            f"{session_type} · {year}", gp_label,
            f"{total_laps}/{total_laps}",
            air, track_w, wind,
            best, d1, avg, "driver avg", cons, "std dev (s)", worst, "driver",
            "status-dot ready", f"SESSION READY — {year} {gp_label} {session_type}",
            standings, "btn-row",
            total_laps, fl_time, fl_drv,
            opts, d1, opts, d2, opts, d1,
            circuit_name, circuit_len,
        )

    def _build_standings(session):
        try:
            laps = session.laps.copy()
            last = (laps.sort_values("LapNumber").groupby("Driver").last()
                        .reset_index().sort_values("Position").head(20))
            fl   = laps["LapTime"].min()
            # Get team colors from session results
            team_colors = {}
            if hasattr(session, 'results') and session.results is not None:
                for _, res in session.results.iterrows():
                    drv = res.get('Abbreviation', res.get('Driver'))
                    team = str(res.get('TeamName', ''))
                    # Map team to color
                    team_color_map = {
                        'Red Bull Racing': '#3671C6',
                        'Mercedes': '#27F4D2',
                        'Ferrari': '#E8002D',
                        'McLaren': '#FF8000',
                        'Aston Martin': '#358C75',
                        'Alpine': '#FF87BC',
                        'Williams': '#64C4FF',
                        'AlphaTauri': '#5E8FAA',
                        'Haas F1 Team': '#B6BABD',
                        'Alfa Romeo': '#00E701',
                        'Sauber': '#00E701',
                    }
                    color = team_color_map.get(team, TEAM_COLORS.get(drv, '#888888'))
                    team_colors[drv] = color
            else:
                team_colors = TEAM_COLORS.copy()
            
            rows = []
            for i, row in enumerate(last.itertuples()):
                drv   = row.Driver
                pos   = int(row.Position) if not pd.isna(row.Position) else i + 1
                comp  = str(getattr(row, "Compound", "H"))
                ci    = comp[0] if comp and comp != "nan" else "H"
                dl    = laps[laps["Driver"] == drv]
                best  = dl["LapTime"].min()
                last_ = getattr(row, "LapTime", None)
                color = team_colors.get(drv, "#888888")
                bs    = _fmt_lap(best.total_seconds() if pd.notna(best) else None)
                ls    = _fmt_lap(last_.total_seconds() if hasattr(last_, "total_seconds") else None)
                rows.append(html.Div(className="driver-row", children=[
                    html.Span(str(pos), className="pos-num"),
                    html.Span(drv, className="driver-tag",
                              style={"borderLeft": f"3px solid {color}", "paddingLeft": "6px"}),
                    html.Div(className="driver-info", children=[
                        html.Span(drv, className="driver-name", style={"color": color}),
                        html.Span(getattr(row, "Team", ""), className="team-name"),
                    ]),
                    html.Div(html.Span(ci, className=f"tyre-badge tyre-{ci}"),
                             style={"textAlign": "right"}),
                    html.Span("—", className="gap-val"),
                    html.Span(ls, className="lap-time"),
                    html.Span(bs, className=f"lap-time {'fastest' if best == fl else 'best'}"),
                ]))
            return rows or [html.Div("No lap data", className="empty-state")]
        except Exception as e:
            return [html.Div(f"Standings error: {e}", className="empty-state")]

    # ── Track map ─────────────────────────────────────────────────────────────
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

    # ── Telemetry — fires on session load AND button clicks ───────────────────
    @app.callback(
        Output("tel-graph",       "figure"),
        Output("tel-chart-title", "children"),
        Input("store-session",    "data"),
        Input("sel-tel-driver",   "value"),
        Input("btn-tel-speed",    "n_clicks"),
        Input("btn-tel-throttle", "n_clicks"),
        Input("btn-tel-brake",    "n_clicks"),
        Input("btn-tel-gear",     "n_clicks"),
        prevent_initial_call=True,
    )
    def update_telemetry(store, tel_driver, sp, th, br, ge):
        if not store: return _empty_fig("Load a session first"), "—"
        driver = tel_driver or store.get("driver1", "VER")
        cmap = {
            "btn-tel-speed":    ("Speed",    "Speed (km/h)", "#E8002D"),
            "btn-tel-throttle": ("Throttle", "Throttle (%)", "#34D399"),
            "btn-tel-brake":    ("Brake",    "Brake",        "#EF4444"),
            "btn-tel-gear":     ("nGear",    "Gear",         "#F59E0B"),
        }
        ch, yl, col = cmap.get(ctx.triggered_id, ("Speed", "Speed (km/h)", "#E8002D"))
        try:
            sess = _get_session(store["year"], store["gp"], store["session_type"])
            lap  = sess.laps.pick_drivers(driver).pick_fastest()
            tel  = lap.get_car_data().add_distance()
            fig  = go.Figure()
            # Convert hex color to rgba for fillcolor
            def hex_to_rgba(hex_col, alpha=0.13):
                hc = hex_col.lstrip('#')
                r, g, b = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
                return f"rgba({r},{g},{b},{alpha})"
            
            fig.add_trace(go.Scatter(
                x=tel["Distance"], y=tel[ch], mode="lines",
                line=dict(color=col, width=1.5),
                fill="tozeroy", fillcolor=hex_to_rgba(col),
                name=driver,
                hovertemplate=f"%{{y:.1f}}<extra>{driver}</extra>",
            ))
            fig.update_layout(**_base_layout(y_title=yl))
            return fig, f"{yl} — {driver}"
        except Exception as e:
            return _empty_fig(str(e)), f"Error: {e}"

    # ── Driver comparison ─────────────────────────────────────────────────────
    @app.callback(
        Output("cmp-graph",  "figure"),
        Output("cmp-d1-name", "children"), Output("cmp-d2-name", "children"),
        Output("cmp-d1-lap", "children"), Output("cmp-d2-lap", "children"),
        Output("cmp-d1-s1",  "children"), Output("cmp-d1-s2",  "children"),
        Output("cmp-d1-s3",  "children"), Output("cmp-d2-s1",  "children"),
        Output("cmp-d2-s2",  "children"), Output("cmp-d2-s3",  "children"),
        Output("cmp-d1-dot", "style"), Output("cmp-d2-dot", "style"),
        Input("store-session", "data"),
        Input("sel-driver1", "value"),
        Input("sel-driver2", "value"),
        prevent_initial_call=True,
    )
    def update_compare(store, driver1, driver2):
        blank = ("—:——.———",) * 2 + ("—",) * 6
        default_dot = {"width": "10px", "height": "10px", "borderRadius": "50%", "background": "rgba(255,255,255,0.18)", "flexShrink": "0"}
        if not store:
            return (_empty_fig(), "—", "—", *blank, default_dot, default_dot)
        try:
            sess = _get_session(store["year"], store["gp"], store["session_type"])
            d1 = driver1 or store.get("driver1", "VER")
            d2 = driver2 or store.get("driver2", "HAM")

            team_color_map = {
                'Red Bull Racing': '#3671C6', 'Mercedes': '#27F4D2',
                'Ferrari': '#E8002D', 'McLaren': '#FF8000',
                'Aston Martin': '#358C75', 'Alpine': '#FF87BC',
                'Williams': '#64C4FF', 'AlphaTauri': '#5E8FAA',
                'Haas F1 Team': '#B6BABD', 'Alfa Romeo': '#00E701',
                'Sauber': '#00E701',
            }
            driver_colors = TEAM_COLORS.copy()
            if hasattr(sess, 'results') and sess.results is not None:
                for _, res in sess.results.iterrows():
                    drv = res.get('Abbreviation', res.get('Driver'))
                    team = str(res.get('TeamName', '')).strip()
                    driver_colors[drv] = team_color_map.get(team, TEAM_COLORS.get(drv, '#888888'))

            c1 = driver_colors.get(d1, TEAM_COLORS.get(d1, '#E8002D'))
            c2 = driver_colors.get(d2, TEAM_COLORS.get(d2, '#3671C6'))

            tel1, tel2, lap1, lap2 = compare_drivers(sess, d1, d2)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tel1["Distance"], y=tel1["Speed"], mode="lines",
                                     line=dict(color=c1, width=1.8), name=d1))
            fig.add_trace(go.Scatter(x=tel2["Distance"], y=tel2["Speed"], mode="lines",
                                     line=dict(color=c2, width=1.8, dash="dot"), name=d2))
            fig.update_layout(**_base_layout(y_title="Speed (km/h)"))

            d1l = _fmt_lap(lap1["LapTime"].total_seconds() if pd.notna(lap1["LapTime"]) else None)
            d2l = _fmt_lap(lap2["LapTime"].total_seconds() if pd.notna(lap2["LapTime"]) else None)
            d1s = [_fmt_sector(lap1.get(f"Sector{i}Time")) for i in [1, 2, 3]]
            d2s = [_fmt_sector(lap2.get(f"Sector{i}Time")) for i in [1, 2, 3]]
            dot1 = {"width": "10px", "height": "10px", "borderRadius": "50%", "background": c1, "flexShrink": "0"}
            dot2 = {"width": "10px", "height": "10px", "borderRadius": "50%", "background": c2, "flexShrink": "0"}
            return (fig, d1, d2, d1l, d2l, *d1s, *d2s, dot1, dot2)
        except Exception as e:
            return (_empty_fig(str(e)), "—", "—", *blank, default_dot, default_dot)

    # ── Replay store ──────────────────────────────────────────────────────────
    @app.callback(
        Output("store-replay-data",   "data"),
        Output("replay-legend",       "children"),
        Output("replay-frame-slider", "max"),
        Output("replay-lap-total",    "children"),
        Input("store-session", "data"),
        prevent_initial_call=True,
    )
    def build_replay_store(store):
        if not store: return None, [], 100, ""
        try:
            session = _get_session(store["year"], store["gp"], store["session_type"])
            data    = _build_replay_data(session)
            if not data:
                return None, [html.Div("No position data", className="empty-state")], 100, ""
            legend = [
                html.Div(className="replay-legend-chip", children=[
                    html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%",
                                    "background": data["colors"].get(d, "#888"),
                                    "flexShrink": "0"}),
                    html.Span(d, style={"fontFamily": _M, "fontSize": "10px",
                                        "color": "rgba(255,255,255,0.6)"}),
                ]) for d in data["drivers"]
            ]
            return data, legend, max(0, data["total"] - 1), f"/ {data['total_laps']}"
        except Exception as e:
            return None, [html.Div(f"Replay error: {e}", className="empty-state")], 100, ""

    # ── Replay frame render ───────────────────────────────────────────────────
    @app.callback(
        Output("replay-graph",   "figure"),
        Output("replay-lap-num", "children"),
        Input("store-replay-data",   "data"),
        Input("replay-frame-slider", "value"),
        prevent_initial_call=True,
    )
    def render_replay_frame(data, frame_idx):
        if not data: return _empty_map("Load a session to see the race replay"), "—"
        idx     = int(frame_idx or 0)
        total   = max(1, data["total"])
        laps    = data["total_laps"]
        lap_now = max(1, min(laps, int(idx / total * laps) + 1))
        return _replay_fig(data, idx), str(lap_now)

    # ── Replay play/pause/reset ───────────────────────────────────────────────
    @app.callback(
        Output("replay-interval",      "disabled"),
        Output("store-replay-playing", "data"),
        Output("replay-play-btn",      "children"),
        Input("replay-play-btn",  "n_clicks"),
        Input("replay-reset-btn", "n_clicks"),
        Input("store-session", "data"),
        State("store-replay-playing", "data"),
        prevent_initial_call=True,
    )
    def toggle_replay(play_clicks, reset_clicks, store_session, is_playing):
        triggered = ctx.triggered_id
        if triggered == "replay-reset-btn":
            return True, False, "▶  Play"
        if triggered == "store-session":
            if not store_session:
                return True, False, "▶  Play"
            return False, True, "⏸  Pause"
        new_playing = not bool(is_playing)
        return (not new_playing), new_playing, ("⏸  Pause" if new_playing else "▶  Play")

    @app.callback(
        Output("replay-frame-slider", "value"),
        Input("replay-interval",  "n_intervals"),
        Input("replay-reset-btn", "n_clicks"),
        Input("store-session", "data"),
        State("replay-frame-slider", "value"),
        State("replay-frame-slider", "max"),
        State("store-replay-playing", "data"),
        prevent_initial_call=True,
    )
    def advance_frame(n_intervals, reset_clicks, store_session, current, max_val, is_playing):
        triggered = ctx.triggered_id
        if triggered == "replay-reset-btn":
            return 0
        if triggered == "store-session":
            if not store_session:
                return 0
            return 0
        if not is_playing:
            return no_update
        nxt = int(current or 0) + 1
        return 0 if nxt > int(max_val or 100) else nxt

    # -- Quick plot buttons --
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
            # Switch to telemetry tab
            return (tel_state or 0) + 1, track_state or 0
        elif tid == "btn-track-map":
            # Switch to track tab
            return tel_state or 0, (track_state or 0) + 1
        return no_update, no_update