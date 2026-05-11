"""layout.py — Cinematic F1 Telemetry Dashboard
Premium UI: full-viewport, Orbitron/Rajdhani typography, glowing race replay,
F1 2025 calendar, dominant track maps.
"""

from dash import dcc, html
from datetime import datetime

# ── Data ──────────────────────────────────────────────────────────────────────

GRP_MAP = {
    "bahrain":      "Bahrain Grand Prix",
    "saudi_arabia": "Saudi Arabian Grand Prix",
    "australia":    "Australian Grand Prix",
    "japan":        "Japanese Grand Prix",
    "china":        "Chinese Grand Prix",
    "miami":        "Miami Grand Prix",
    "imola":        "Emilia Romagna Grand Prix",
    "monaco":       "Monaco Grand Prix",
    "spain":        "Spanish Grand Prix",
    "canada":       "Canadian Grand Prix",
    "austria":      "Austrian Grand Prix",
    "britain":      "British Grand Prix",
    "hungary":      "Hungarian Grand Prix",
    "belgium":      "Belgian Grand Prix",
    "netherlands":  "Dutch Grand Prix",
    "italy":        "Italian Grand Prix",
    "azerbaijan":   "Azerbaijan Grand Prix",
    "singapore":    "Singapore Grand Prix",
    "usa":          "United States Grand Prix",
    "mexico":       "Mexico City Grand Prix",
    "brazil":       "São Paulo Grand Prix",
    "las_vegas":    "Las Vegas Grand Prix",
    "qatar":        "Qatar Grand Prix",
    "abu_dhabi":    "Abu Dhabi Grand Prix",
}

SESSION_TYPES  = ["R", "Q", "FP1", "FP2", "FP3", "S"]
SESSION_LABELS = {"R": "Race", "Q": "Qualifying", "FP1": "FP1",
                  "FP2": "FP2", "FP3": "FP3", "S": "Sprint"}

_CURRENT_YEAR = datetime.now().year
YEARS = list(range(_CURRENT_YEAR, 2017, -1))

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

DRIVERS = sorted([
    "ANT", "PIA", "LEC", "RUS", "NOR", "HAM",
    "GAS", "VER", "LAW", "OCO", "ALO", "STR",
    "TSU", "ZHO", "BOT", "HUL", "MAG", "ALB",
    "HAD", "BEA", "COL", "DOO",
])

# ── 2025 F1 Calendar ──────────────────────────────────────────────────────────
F1_CALENDAR_2025 = [
    {"round": 1,  "name": "Australian Grand Prix",       "circuit": "Albert Park",             "date": "2025-03-16", "country": "🇦🇺", "key": "australia"},
    {"round": 2,  "name": "Chinese Grand Prix",          "circuit": "Shanghai International",  "date": "2025-03-23", "country": "🇨🇳", "key": "china"},
    {"round": 3,  "name": "Japanese Grand Prix",         "circuit": "Suzuka",                  "date": "2025-04-06", "country": "🇯🇵", "key": "japan"},
    {"round": 4,  "name": "Bahrain Grand Prix",          "circuit": "Bahrain International",   "date": "2025-04-13", "country": "🇧🇭", "key": "bahrain"},
    {"round": 5,  "name": "Saudi Arabian Grand Prix",    "circuit": "Jeddah Corniche",         "date": "2025-04-20", "country": "🇸🇦", "key": "saudi_arabia"},
    {"round": 6,  "name": "Miami Grand Prix",            "circuit": "Hard Rock Stadium",       "date": "2025-05-04", "country": "🇺🇸", "key": "miami"},
    {"round": 7,  "name": "Emilia Romagna Grand Prix",   "circuit": "Autodromo Imola",         "date": "2025-05-18", "country": "🇮🇹", "key": "imola"},
    {"round": 8,  "name": "Monaco Grand Prix",           "circuit": "Circuit de Monaco",       "date": "2025-05-25", "country": "🇲🇨", "key": "monaco"},
    {"round": 9,  "name": "Spanish Grand Prix",          "circuit": "Circuit de Barcelona",    "date": "2025-06-01", "country": "🇪🇸", "key": "spain"},
    {"round": 10, "name": "Canadian Grand Prix",         "circuit": "Circuit Gilles Villeneuve","date": "2025-06-15","country": "🇨🇦", "key": "canada"},
    {"round": 11, "name": "Austrian Grand Prix",         "circuit": "Red Bull Ring",           "date": "2025-06-29", "country": "🇦🇹", "key": "austria"},
    {"round": 12, "name": "British Grand Prix",          "circuit": "Silverstone",             "date": "2025-07-06", "country": "🇬🇧", "key": "britain"},
    {"round": 13, "name": "Belgian Grand Prix",          "circuit": "Spa-Francorchamps",       "date": "2025-07-27", "country": "🇧🇪", "key": "belgium"},
    {"round": 14, "name": "Hungarian Grand Prix",        "circuit": "Hungaroring",             "date": "2025-08-03", "country": "🇭🇺", "key": "hungary"},
    {"round": 15, "name": "Dutch Grand Prix",            "circuit": "Circuit Zandvoort",       "date": "2025-08-31", "country": "🇳🇱", "key": "netherlands"},
    {"round": 16, "name": "Italian Grand Prix",          "circuit": "Autodromo di Monza",      "date": "2025-09-07", "country": "🇮🇹", "key": "italy"},
    {"round": 17, "name": "Azerbaijan Grand Prix",       "circuit": "Baku City Circuit",       "date": "2025-09-21", "country": "🇦🇿", "key": "azerbaijan"},
    {"round": 18, "name": "Singapore Grand Prix",        "circuit": "Marina Bay Street",       "date": "2025-10-05", "country": "🇸🇬", "key": "singapore"},
    {"round": 19, "name": "United States Grand Prix",    "circuit": "Circuit of the Americas", "date": "2025-10-19", "country": "🇺🇸", "key": "usa"},
    {"round": 20, "name": "Mexico City Grand Prix",      "circuit": "Autódromo Hermanos Rodríguez","date": "2025-10-26","country": "🇲🇽","key": "mexico"},
    {"round": 21, "name": "São Paulo Grand Prix",        "circuit": "Autodromo Interlagos",    "date": "2025-11-09", "country": "🇧🇷", "key": "brazil"},
    {"round": 22, "name": "Las Vegas Grand Prix",        "circuit": "Las Vegas Strip Circuit", "date": "2025-11-22", "country": "🇺🇸", "key": "las_vegas"},
    {"round": 23, "name": "Qatar Grand Prix",            "circuit": "Lusail International",    "date": "2025-11-30", "country": "🇶🇦", "key": "qatar"},
    {"round": 24, "name": "Abu Dhabi Grand Prix",        "circuit": "Yas Marina Circuit",      "date": "2025-12-07", "country": "🇦🇪", "key": "abu_dhabi"},
]

CIRCUIT_INFO = {
    "bahrain":      {"name": "Bahrain Grand Prix",       "location": "Sakhir",          "length": "5.412 km", "corners": "15", "first_gp": "2004", "races": "19", "lap_record": "1:31.447", "record_holder": "Pedro de la Rosa (2005)",      "description": "Season opener with high-speed corners in the desert."},
    "saudi_arabia": {"name": "Saudi Arabian Grand Prix", "location": "Jeddah",          "length": "6.174 km", "corners": "27", "first_gp": "2021", "races": "3",  "lap_record": "1:30.734", "record_holder": "Lewis Hamilton (2021)",         "description": "Street circuit with the fastest corner in F1 at over 320 km/h."},
    "australia":    {"name": "Australian Grand Prix",    "location": "Melbourne",        "length": "5.278 km", "corners": "16", "first_gp": "1996", "races": "25", "lap_record": "1:24.125", "record_holder": "Michael Schumacher (2004)",    "description": "Albert Park blends street and permanent sections under changeable skies."},
    "japan":        {"name": "Japanese Grand Prix",      "location": "Suzuka",           "length": "5.807 km", "corners": "18", "first_gp": "1987", "races": "30", "lap_record": "1:30.983", "record_holder": "Lewis Hamilton (2019)",         "description": "Iconic figure-8 layout demanding full commitment through high-speed corners."},
    "china":        {"name": "Chinese Grand Prix",       "location": "Shanghai",         "length": "5.451 km", "corners": "16", "first_gp": "2004", "races": "16", "lap_record": "1:32.238", "record_holder": "Michael Schumacher (2004)",    "description": "Long straights and heavy braking zones reward precision strategy."},
    "miami":        {"name": "Miami Grand Prix",         "location": "Miami Gardens",    "length": "5.412 km", "corners": "19", "first_gp": "2022", "races": "2",  "lap_record": "1:29.708", "record_holder": "Max Verstappen (2023)",         "description": "Street circuit around Hard Rock Stadium in the heart of Miami."},
    "imola":        {"name": "Emilia Romagna Grand Prix","location": "Imola",            "length": "4.909 km", "corners": "19", "first_gp": "1980", "races": "28", "lap_record": "1:15.484", "record_holder": "Lewis Hamilton (2020)",         "description": "Historic Autodromo Enzo e Dino Ferrari with high-speed corners."},
    "monaco":       {"name": "Monaco Grand Prix",        "location": "Monte Carlo",      "length": "3.337 km", "corners": "19", "first_gp": "1950", "races": "69", "lap_record": "1:10.166", "record_holder": "Lewis Hamilton (2021)",         "description": "The most prestigious race on Monaco's narrow streets."},
    "spain":        {"name": "Spanish Grand Prix",       "location": "Barcelona",        "length": "4.675 km", "corners": "16", "first_gp": "1991", "races": "30", "lap_record": "1:12.272", "record_holder": "Max Verstappen (2021)",         "description": "Technical development circuit with varied corners at all speeds."},
    "canada":       {"name": "Canadian Grand Prix",      "location": "Montreal",         "length": "4.361 km", "corners": "14", "first_gp": "1978", "races": "42", "lap_record": "1:13.078", "record_holder": "Valtteri Bottas (2019)",        "description": "Circuit Gilles Villeneuve featuring the famous Wall of Champions."},
    "austria":      {"name": "Austrian Grand Prix",      "location": "Spielberg",        "length": "4.318 km", "corners": "10", "first_gp": "1970", "races": "34", "lap_record": "1:05.619", "record_holder": "Carlos Sainz (2020)",           "description": "Red Bull Ring's high-altitude location provides unique downforce challenges."},
    "britain":      {"name": "British Grand Prix",       "location": "Silverstone",      "length": "5.891 km", "corners": "18", "first_gp": "1950", "races": "71", "lap_record": "1:27.097", "record_holder": "Max Verstappen (2020)",         "description": "Home of British motorsport with fast, fearless corners."},
    "hungary":      {"name": "Hungarian Grand Prix",     "location": "Budapest",         "length": "4.381 km", "corners": "14", "first_gp": "1986", "races": "37", "lap_record": "1:16.627", "record_holder": "Lewis Hamilton (2020)",         "description": "Hungaroring's tight layout makes overtaking difficult and strategy crucial."},
    "belgium":      {"name": "Belgian Grand Prix",       "location": "Spa-Francorchamps","length": "7.004 km", "corners": "19", "first_gp": "1950", "races": "66", "lap_record": "1:46.286", "record_holder": "Valtteri Bottas (2018)",        "description": "Longest circuit on the calendar with the legendary Eau Rouge."},
    "netherlands":  {"name": "Dutch Grand Prix",         "location": "Zandvoort",        "length": "4.259 km", "corners": "14", "first_gp": "1952", "races": "33", "lap_record": "1:11.097", "record_holder": "Lewis Hamilton (2021)",         "description": "Sandy dunes circuit with high-speed banking and passionate crowds."},
    "italy":        {"name": "Italian Grand Prix",       "location": "Monza",            "length": "5.793 km", "corners": "11", "first_gp": "1950", "races": "73", "lap_record": "1:21.046", "record_holder": "Rubens Barrichello (2004)",     "description": "Temple of speed — minimal downforce, maximum straight-line velocity."},
    "azerbaijan":   {"name": "Azerbaijan Grand Prix",    "location": "Baku",             "length": "6.003 km", "corners": "20", "first_gp": "2016", "races": "6",  "lap_record": "1:43.009", "record_holder": "Charles Leclerc (2019)",        "description": "Baku City Circuit combines castles, sea views and raw speed."},
    "singapore":    {"name": "Singapore Grand Prix",     "location": "Marina Bay",       "length": "5.063 km", "corners": "23", "first_gp": "2008", "races": "14", "lap_record": "1:41.905", "record_holder": "Kevin Magnussen (2018)",        "description": "Nocturnal street racing under the neon lights of Singapore."},
    "usa":          {"name": "United States Grand Prix", "location": "Austin",           "length": "5.513 km", "corners": "20", "first_gp": "2012", "races": "10", "lap_record": "1:36.169", "record_holder": "Charles Leclerc (2019)",        "description": "COTA features the challenging Esses and sweeping high-speed corners."},
    "mexico":       {"name": "Mexico City Grand Prix",   "location": "Mexico City",      "length": "4.304 km", "corners": "17", "first_gp": "1963", "races": "22", "lap_record": "1:17.774", "record_holder": "Valtteri Bottas (2018)",        "description": "High altitude demands careful engine management and aero tuning."},
    "brazil":       {"name": "São Paulo Grand Prix",     "location": "São Paulo",        "length": "4.309 km", "corners": "15", "first_gp": "1973", "races": "39", "lap_record": "1:10.540", "record_holder": "Valtteri Bottas (2018)",        "description": "Interlagos' downhill start and challenging corners deliver drama."},
    "las_vegas":    {"name": "Las Vegas Grand Prix",     "location": "Las Vegas",        "length": "6.201 km", "corners": "17", "first_gp": "2023", "races": "1",  "lap_record": "1:35.490", "record_holder": "Oscar Piastri (2023)",          "description": "The Strip circuit brings F1 to neon Las Vegas with long straights."},
    "qatar":        {"name": "Qatar Grand Prix",         "location": "Lusail",           "length": "5.419 km", "corners": "16", "first_gp": "2021", "races": "3",  "lap_record": "1:23.196", "record_holder": "Max Verstappen (2023)",         "description": "Lusail's night race with smooth, flowing high-speed corners."},
    "abu_dhabi":    {"name": "Abu Dhabi Grand Prix",     "location": "Yas Island",       "length": "5.281 km", "corners": "21", "first_gp": "2009", "races": "14", "lap_record": "1:26.103", "record_holder": "Max Verstappen (2021)",         "description": "Season finale at Yas Marina with the iconic hotel backdrop."},
}

TEAM_INFO = {
    "Red Bull": {
        "color": "#3671C6", "drivers": ["VER", "PER"],
        "description": "A championship-contending team with a balanced package and relentless race pace.",
        "championships": "6", "drivers_championships": "8",
        "wins": "115", "poles": "103", "founded": "2005", "base": "Milton Keynes, UK",
    },
    "Mercedes": {
        "color": "#27F4D2", "drivers": ["HAM", "RUS"],
        "description": "Hybrid-era powerhouse known for strategic excellence and technical brilliance.",
        "championships": "8", "drivers_championships": "8",
        "wins": "125", "poles": "137", "founded": "2010", "base": "Brackley, UK",
    },
    "Ferrari": {
        "color": "#E8002D", "drivers": ["LEC", "SAI"],
        "description": "The most iconic team in motorsport — 16 constructors' titles and counting.",
        "championships": "16", "drivers_championships": "15",
        "wins": "243", "poles": "252", "founded": "1929", "base": "Maranello, Italy",
    },
    "McLaren": {
        "color": "#FF8000", "drivers": ["NOR", "PIA"],
        "description": "British squad surging back to the front with inspired development.",
        "championships": "8", "drivers_championships": "12",
        "wins": "183", "poles": "156", "founded": "1963", "base": "Woking, UK",
    },
    "Aston Martin": {
        "color": "#358C75", "drivers": ["ALO", "STR"],
        "description": "Blending Alonso's experience with strong engineering in Silverstone.",
        "championships": "0", "drivers_championships": "0",
        "wins": "0", "poles": "1", "founded": "2021", "base": "Silverstone, UK",
    },
    "Alpine": {
        "color": "#FF87BC", "drivers": ["OCO", "GAS"],
        "description": "French team focused on qualifying pace and mid-season development.",
        "championships": "2", "drivers_championships": "2",
        "wins": "21", "poles": "20", "founded": "2021", "base": "Enstone, UK",
    },
    "Williams": {
        "color": "#64C4FF", "drivers": ["ALB", "SAR"],
        "description": "Historic constructor rebuilding towards the front with young talent.",
        "championships": "9", "drivers_championships": "7",
        "wins": "114", "poles": "128", "founded": "1977", "base": "Grove, UK",
    },
    "AlphaTauri": {
        "color": "#5E8FAA", "drivers": ["TSU", "LAW"],
        "description": "Driver development programme that has launched world champions.",
        "championships": "0", "drivers_championships": "0",
        "wins": "1", "poles": "1", "founded": "2020", "base": "Faenza, Italy",
    },
    "Haas": {
        "color": "#B6BABD", "drivers": ["HUL", "MAG"],
        "description": "Lean American outfit maximising performance through efficient engineering.",
        "championships": "0", "drivers_championships": "0",
        "wins": "0", "poles": "0", "founded": "2016", "base": "Kannapolis, USA",
    },
    "Alfa Romeo": {
        "color": "#00E701", "drivers": ["BOT", "ZHO"],
        "description": "Swiss-based team blending veteran stability with technical improvement.",
        "championships": "0", "drivers_championships": "0",
        "wins": "1", "poles": "1", "founded": "2019", "base": "Hinwil, Switzerland",
    },
}


# ── Helper components ─────────────────────────────────────────────────────────

def _driver_options():
    return [{"label": d, "value": d,
             "title": TEAM_COLORS.get(d, "#888888")} for d in DRIVERS]


def _label(text):
    return html.Div(text, className="field-label")


def _stat_card(val_id, sub_id, label):
    return html.Div([
        html.Div(label, className="stat-label"),
        html.Div("—",   id=val_id, className="stat-val"),
        html.Div("—",   id=sub_id, className="stat-sub"),
    ], className="stat-card")


def _graph_tooltip(title, desc):
    """Game-style popup tooltip: hover the red ? to see an explanation."""
    return html.Div(className="graph-info-tip", children=[
        html.Div("?", className="graph-info-icon"),
        html.Div(className="graph-info-popup", children=[
            html.Div(title, className="graph-info-title"),
            html.Div(desc, className="graph-info-desc"),
        ]),
    ])


# ── Panels ────────────────────────────────────────────────────────────────────

def _session_panel():
    return html.Div(id="panel-session", className="panel active", children=[

        # ── HERO + LOADER (side by side) ─────────────────────────────────────
        html.Div(className="sh-layout", children=[

            # Left: identity — 38% width
            html.Div(className="sh-identity", children=[
                html.Div("FORMULA 1 TELEMETRY", className="sh-eyebrow"),
                html.Div("SELECT SESSION", className="sh-title", id="session-hero-title"),
                html.Div(
                    "Choose a Grand Prix, season and session type to begin analysis.",
                    className="sh-subtitle", id="session-hero-sub",
                ),
                html.Div(className="sh-divider"),
                html.Div(className="sh-status", children=[
                    html.Div(className="sh-status-dot", id="session-hero-dot"),
                    html.Span("AWAITING SESSION", id="session-hero-status",
                              className="sh-status-label"),
                ]),
            ]),

            # Right: loader form — 62% width
            html.Div(className="sh-form-card", children=[

                # Three field columns + button
                html.Div(className="sh-fields", children=[
                    html.Div(className="sh-field", children=[
                        html.Div("SEASON", className="sh-field-label"),
                        html.Div(className="f1-dropdown", children=[
                            dcc.Dropdown(
                                id="sel-year",
                                options=[{"label": str(y), "value": y} for y in YEARS],
                                value=_CURRENT_YEAR, clearable=False, searchable=False,
                            ),
                        ]),
                    ]),
                    html.Div(className="sh-field sh-field-wide", children=[
                        html.Div("GRAND PRIX", className="sh-field-label"),
                        html.Div(className="f1-dropdown", children=[
                            dcc.Dropdown(
                                id="sel-gp",
                                options=[{"label": v, "value": k} for k, v in GRP_MAP.items()],
                                value="japan", clearable=False,
                            ),
                        ]),
                    ]),
                    html.Div(className="sh-field", children=[
                        html.Div("SESSION TYPE", className="sh-field-label"),
                        html.Div(className="f1-dropdown", children=[
                            dcc.Dropdown(
                                id="sel-session",
                                options=[{"label": SESSION_LABELS[s], "value": s}
                                         for s in SESSION_TYPES],
                                value="R", clearable=False, searchable=False,
                            ),
                        ]),
                    ]),
                    html.Div(className="sh-field", children=[
                        html.Div("FOCUS DRIVER", className="sh-field-label"),
                        html.Div(className="f1-dropdown", children=[
                            dcc.Dropdown(
                                id="sel-focus-driver",
                                options=[{"label": d, "value": d} for d in DRIVERS],
                                value=None, clearable=True,
                                placeholder="All drivers",
                                searchable=True,
                            ),
                        ]),
                    ]),
                    html.Div(className="sh-field sh-field-btn", children=[
                        html.Div("\u00a0", className="sh-field-label"),   # spacer
                        html.Button("LOAD SESSION", id="load-btn",
                                    className="load-btn sh-load-btn", n_clicks=0),
                    ]),
                ]),

                # Quick plots strip inside the form card
                html.Div(className="sh-qp-strip", children=[
                    html.Div("QUICK PLOTS", className="sh-qp-label"),
                    html.Div(id="plot-btns", className="sh-qp-btns disabled-plots", children=[
                        html.Button("Speed Trace",    id="btn-speed-trace",
                                    className="qp-btn", n_clicks=0),
                        html.Button("Full Telemetry", id="btn-tel-panel",
                                    className="qp-btn", n_clicks=0),
                        html.Button("Lap Times",      id="btn-lap-times",
                                    className="qp-btn", n_clicks=0),
                        html.Button("Track Map",      id="btn-track-map",
                                    className="qp-btn", n_clicks=0),
                        html.Button("Tyre Usage",     id="btn-compounds",
                                    className="qp-btn", n_clicks=0),
                    ]),
                ]),
            ]),
        ]),

        # ── STATS BAR ────────────────────────────────────────────────────────
        html.Div(className="sstat-bar", children=[
            html.Div(className="sstat-cell", children=[
                html.Div("BEST LAP",     className="sstat-label"),
                html.Div("—", id="stat-best",     className="sstat-val sstat-purple"),
                html.Div("—", id="stat-best-drv", className="sstat-sub"),
            ]),
            html.Div(className="sstat-sep"),
            html.Div(className="sstat-cell", children=[
                html.Div("AVG LAP",      className="sstat-label"),
                html.Div("—", id="stat-avg",      className="sstat-val"),
                html.Div("—", id="stat-avg-sub",  className="sstat-sub"),
            ]),
            html.Div(className="sstat-sep"),
            html.Div(className="sstat-cell", children=[
                html.Div("CONSISTENCY",  className="sstat-label"),
                html.Div("—", id="stat-cons",     className="sstat-val"),
                html.Div("—", id="stat-cons-sub", className="sstat-sub"),
            ]),
            html.Div(className="sstat-sep"),
            html.Div(className="sstat-cell", children=[
                html.Div("WORST LAP",    className="sstat-label"),
                html.Div("—", id="stat-worst",     className="sstat-val"),
                html.Div("—", id="stat-worst-sub", className="sstat-sub"),
            ]),
        ]),

        # ── FOCUSED DRIVER BANNER (shown after load if a driver is selected) ──
        html.Div(id="focus-driver-banner", className="focus-banner", style={"display": "none"},
                 children=[
            html.Div(className="focus-banner-inner", children=[
                html.Div(className="focus-banner-left", children=[
                    html.Div(id="focus-driver-dot", className="focus-driver-dot"),
                    html.Div(className="focus-banner-text", children=[
                        html.Div("FOCUS DRIVER", className="focus-eyebrow"),
                        html.Div("—", id="focus-driver-name", className="focus-driver-code"),
                    ]),
                ]),
                html.Div(className="focus-banner-stats", children=[
                    html.Div(className="focus-stat", children=[
                        html.Div("BEST LAP",    className="focus-stat-label"),
                        html.Div("—", id="focus-best-lap",   className="focus-stat-val focus-purple"),
                    ]),
                    html.Div(className="focus-stat-sep"),
                    html.Div(className="focus-stat", children=[
                        html.Div("AVG LAP",     className="focus-stat-label"),
                        html.Div("—", id="focus-avg-lap",    className="focus-stat-val"),
                    ]),
                    html.Div(className="focus-stat-sep"),
                    html.Div(className="focus-stat", children=[
                        html.Div("CONSISTENCY", className="focus-stat-label"),
                        html.Div("—", id="focus-cons",       className="focus-stat-val"),
                    ]),
                    html.Div(className="focus-stat-sep"),
                    html.Div(className="focus-stat", children=[
                        html.Div("WORST LAP",   className="focus-stat-label"),
                        html.Div("—", id="focus-worst-lap",  className="focus-stat-val"),
                    ]),
                ]),
                html.Div("STATS LOCKED TO THIS DRIVER — ALL ANALYSIS MODULES FOLLOW",
                         className="focus-banner-hint"),
            ]),
        ]),

        # ── ANALYSIS MODULES ─────────────────────────────────────────────────
        html.Div(className="amod-section", children=[
            html.Div(className="amod-header", children=[
                html.Div("ANALYSIS MODULES", className="amod-title"),
                html.Div("Select a module to open", className="amod-hint"),
            ]),
            html.Div(className="amod-grid", children=[

                html.Div(id="module-track-map", className="amod-card", n_clicks=0, children=[
                    html.Div(className="amod-card-top", children=[
                        html.Div(className="amod-accent amod-accent-cyan"),
                        html.Div("TRACK MAP", className="amod-card-label"),
                    ]),
                    html.Div("Circuit Layout", className="amod-card-name"),
                    html.Div("Speed-colored circuit trace with corner annotations.",
                             className="amod-card-desc"),
                    html.Div("OPEN", className="amod-card-cta"),
                ]),

                html.Div(id="module-telemetry", className="amod-card", n_clicks=0, children=[
                    html.Div(className="amod-card-top", children=[
                        html.Div(className="amod-accent amod-accent-green"),
                        html.Div("TELEMETRY", className="amod-card-label"),
                    ]),
                    html.Div("Driver Data", className="amod-card-name"),
                    html.Div("Speed, throttle, brake and gear traces across a lap.",
                             className="amod-card-desc"),
                    html.Div("OPEN", className="amod-card-cta"),
                ]),

                html.Div(id="module-compare", className="amod-card", n_clicks=0, children=[
                    html.Div(className="amod-card-top", children=[
                        html.Div(className="amod-accent amod-accent-amber"),
                        html.Div("COMPARE", className="amod-card-label"),
                    ]),
                    html.Div("Head to Head", className="amod-card-name"),
                    html.Div("Overlay two drivers' fastest laps to find delta.",
                             className="amod-card-desc"),
                    html.Div("OPEN", className="amod-card-cta"),
                ]),

                html.Div(id="module-replay", className="amod-card amod-card-primary",
                         n_clicks=0, children=[
                    html.Div(className="amod-card-top", children=[
                        html.Div(className="amod-accent amod-accent-red"),
                        html.Div("RACE REPLAY", className="amod-card-label"),
                    ]),
                    html.Div("Live Positions", className="amod-card-name"),
                    html.Div("Animated car positions on the circuit with leaderboard.",
                             className="amod-card-desc"),
                    html.Div("OPEN", className="amod-card-cta"),
                ]),
            ]),
        ]),
    ])


def _standings_panel():
    return html.Div(id="panel-standings", className="panel", children=[

        # ── PAGE HEADER ───────────────────────────────────────────────────────
        html.Div(className="stnd-page-header", children=[
            html.Div(className="stnd-page-header-left", children=[
                html.Div("LIVE SESSION", className="stnd-eyebrow"),
                html.Div("RACE ORDER", className="stnd-page-title"),
            ]),
            html.Div(className="stnd-legend", children=[
                html.Div(className="stnd-leg-item", children=[
                    html.Div(className="stnd-leg-pip stnd-pip-purple"),
                    html.Span("FASTEST LAP"),
                ]),
                html.Div(className="stnd-leg-item", children=[
                    html.Div(className="stnd-leg-pip stnd-pip-green"),
                    html.Span("PERSONAL BEST"),
                ]),
                html.Div(className="stnd-leg-item", children=[
                    html.Div(className="stnd-leg-pip stnd-pip-dim"),
                    html.Span("NORMAL"),
                ]),
            ]),
        ]),

        # ── STANDINGS BODY ────────────────────────────────────────────────────
        # Callback fills #standings-body with .stnd-row divs
        html.Div(id="standings-body", className="stnd-list", children=[

            # ── Empty state ──────────────────────────────────────────────────
            html.Div(className="stnd-empty", children=[
                # Geometric "no data" graphic — pure CSS, no emoji
                html.Div(className="stnd-empty-graphic", children=[
                    html.Div(className="seg seg-1"),
                    html.Div(className="seg seg-2"),
                    html.Div(className="seg seg-3"),
                    html.Div(className="seg seg-4"),
                    html.Div(className="seg seg-5"),
                ]),
                html.Div("NO SESSION LOADED", className="stnd-empty-title"),
                html.Div("Load a session from the Session tab to populate race order.",
                         className="stnd-empty-body"),
            ]),
        ]),
    ])


def _track_panel():
    return html.Div(id="panel-track", className="panel", children=[
        html.Div(className="track-panel", children=[
            html.Div(className="track-svg-wrap", children=[
                dcc.Graph(
                    id="track-map-graph",
                    config={"displayModeBar": False, "staticPlot": False},
                    style={"height": "520px", "width": "100%"},
                ),
            ]),
            html.Div(className="track-side", children=[
                html.Div(className="stat-card", children=[
                    html.Div(className="chart-title-row", children=[
                        html.Div("Circuit", className="stat-label"),
                        _graph_tooltip("TRACK MAP",
                                       "Shows the circuit layout. Colors represent speed: "
                                       "purple/red = fast sections, yellow = slow corners. "
                                       "Hover any point for exact km/h."),
                    ]),
                    html.Div("—", id="circuit-name", className="stat-val",
                             style={"fontSize": "16px"}),
                    html.Div("—", id="circuit-len",  className="stat-sub"),
                ]),
                html.Div(className="stat-card", children=[
                    html.Div("Total Laps",    className="stat-label"),
                    html.Div("—", id="total-laps-stat", className="stat-val"),
                    html.Div("race laps",     className="stat-sub"),
                ]),
                html.Div(className="stat-card", children=[
                    html.Div("Fastest",       className="stat-label"),
                    html.Div("—", id="fastest-stat",     className="stat-val fastest-val"),
                    html.Div("—", id="fastest-drv-stat", className="stat-sub"),
                ]),
                html.Div(className="stat-card", children=[
                    html.Div("Sectors", className="stat-label"),
                    html.Div(className="sector-row", children=[
                        html.Div(className="sector-col", children=[
                            html.Div("S1", className="sec-label sec-1"),
                            html.Div("—", id="sec1-val", className="sec-val"),
                        ]),
                        html.Div(className="sector-col", children=[
                            html.Div("S2", className="sec-label sec-2"),
                            html.Div("—", id="sec2-val", className="sec-val"),
                        ]),
                        html.Div(className="sector-col", children=[
                            html.Div("S3", className="sec-label sec-3"),
                            html.Div("—", id="sec3-val", className="sec-val"),
                        ]),
                    ]),
                    html.Div(className="sector-bands", children=[
                        html.Div(className="sb sb-1"),
                        html.Div(className="sb sb-2"),
                        html.Div(className="sb sb-3"),
                    ]),
                ]),
            ]),
        ]),
    ])


def _telemetry_panel():
    return html.Div(id="panel-telemetry", className="panel", children=[
        html.Div(className="loader-grid", style={"gridTemplateColumns": "repeat(2, 1fr)"}, children=[
            html.Div(className="field-group", children=[
                _label("Driver"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(id="sel-tel-driver", options=[], value=None,
                                 clearable=False, placeholder="Select driver"),
                ]),
            ]),
        ]),
        html.Div(className="chart-wrap", style={"minHeight": "340px"}, children=[
            html.Div(className="chart-title-row", children=[
                html.Div("Speed Trace — Load a session first",
                         id="tel-chart-title", className="chart-title"),
                _graph_tooltip("TELEMETRY TRACE",
                               "X-axis = distance around the lap (m). "
                               "Y-axis = the selected metric. Use the buttons below to "
                               "switch between Speed, Throttle, Brake and Gear. "
                               "Dips show braking zones; peaks show top speed on straights."),
            ]),
            dcc.Graph(id="tel-graph", config={"displayModeBar": False},
                      style={"height": "290px"}),
        ]),
        html.Div(className="btn-row", style={"marginTop": "14px"}, children=[
            html.Button("Speed",    id="btn-tel-speed",
                        className="outline-btn active", n_clicks=0),
            html.Button("Throttle", id="btn-tel-throttle",
                        className="outline-btn", n_clicks=0),
            html.Button("Brake",    id="btn-tel-brake",
                        className="outline-btn", n_clicks=0),
            html.Button("Gear",     id="btn-tel-gear",
                        className="outline-btn", n_clicks=0),
        ]),
        html.Div(className="chart-wrap", style={"minHeight": "240px", "marginTop": "18px"}, children=[
            html.Div(className="chart-title-row", children=[
                html.Div("Tyre Degradation — Stint pace by compound",
                         id="tel-tyre-title", className="chart-title"),
                _graph_tooltip("TYRE DEGRADATION",
                               "Lap times for each stint and compound. "
                               "Use this to see how a tyre set evolves over the lap set."),
            ]),
            dcc.Graph(id="tel-tyre-graph", config={"displayModeBar": False},
                      style={"height": "200px"}),
        ]),
        html.Div(id="tel-stint-summary",
                 style={"marginTop": "12px", "fontSize": "13px", "lineHeight": "1.5", "color": "rgba(255,255,255,0.82)"}),
    ])


def _compare_panel():
    drv_opts = _driver_options()

    def _card(dot_id, name_id, lap_id, s1_id, s2_id, s3_id):
        return html.Div(className="driver-select-card", children=[
            html.Div(className="ds-header", children=[
                html.Div(id=dot_id, className="driver-dot",
                         style={"width": "12px", "height": "12px",
                                "borderRadius": "50%", "background": "#888888",
                                "flexShrink": "0",
                                "boxShadow": "0 0 10px currentColor"}),
                html.Span("—", id=name_id, className="ds-label"),
            ]),
            _label("Fastest lap"),
            html.Div("—:——.———", id=lap_id, className="cmp-lap-time"),
            html.Div(className="sector-bands"),
            html.Div(className="cmp-sectors", children=[
                html.Div([html.Div("S1", className="sec-val"),
                          html.Div("—", id=s1_id, className="sec-label sec-1")]),
                html.Div([html.Div("S2", className="sec-val"),
                          html.Div("—", id=s2_id, className="sec-label sec-2")]),
                html.Div([html.Div("S3", className="sec-val"),
                          html.Div("—", id=s3_id, className="sec-label sec-3")]),
            ]),
        ])

    return html.Div(id="panel-compare", className="panel", children=[
        html.Div(className="loader-row", style={"marginBottom": "20px"}, children=[
            html.Div(className="field-group", style={"flex": "1"}, children=[
                _label("Driver 1"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(id="sel-driver1", options=drv_opts,
                                 value="VER", clearable=False,
                                 placeholder="Select driver"),
                ]),
            ]),
            html.Div(className="field-group", style={"flex": "1"}, children=[
                _label("Driver 2"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(id="sel-driver2", options=drv_opts,
                                 value="HAM", clearable=False,
                                 placeholder="Select driver"),
                ]),
            ]),
        ]),
        html.Div(className="compare-grid", children=[
            _card("cmp-d1-dot", "cmp-d1-name", "cmp-d1-lap",
                  "cmp-d1-s1", "cmp-d1-s2", "cmp-d1-s3"),
            _card("cmp-d2-dot", "cmp-d2-name", "cmp-d2-lap",
                  "cmp-d2-s1", "cmp-d2-s2", "cmp-d2-s3"),
        ]),
        html.Div(className="chart-wrap", style={"minHeight": "300px"}, children=[
            html.Div(className="chart-title-row", children=[
                html.Div("Lap Delta — Driver 1 vs Driver 2",
                         className="chart-title"),
                _graph_tooltip("LAP DELTA",
                               "Shows the time gap between the two fastest laps as "
                               "they progress around the circuit. Positive values mean "
                               "Driver 1 is ahead."),
            ]),
            dcc.Graph(id="cmp-graph", config={"displayModeBar": False},
                      style={"height": "250px"}),
        ]),
    ])


def _circuits_panel():
    return html.Div(id="panel-circuits", className="panel", children=[
        html.Div(className="loader-grid", style={"gridTemplateColumns": "1fr"}, children=[
            html.Div(className="field-group", children=[
                _label("Circuit"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(
                        id="sel-circuit",
                        options=[{"label": data["name"], "value": key}
                                 for key, data in CIRCUIT_INFO.items()],
                        value="japan", clearable=False,
                    ),
                ]),
            ]),
        ]),
        html.Div(className="stats-section", children=[
            html.Div("Circuit Details", className="chart-title"),
            html.Div(className="stats-grid", style={"marginTop": "14px"}, children=[
                _stat_card("circuit-length", "circuit-length-sub", "Length"),
                _stat_card("circuit-corners", "circuit-corners-sub", "Corners"),
                _stat_card("circuit-firstgp", "circuit-firstgp-sub", "First GP"),
                _stat_card("circuit-races", "circuit-races-sub", "Races"),
            ]),
            html.Div(className="stats-grid", style={"marginTop": "12px"}, children=[
                _stat_card("circuit-best-lap", "circuit-best-driver", "Best Lap"),
                _stat_card("circuit-lap-record", "circuit-record-holder", "Lap Record"),
                html.Div(className="circuit-description", id="circuit-description",
                         style={"gridColumn": "1 / -1", "paddingTop": "10px"}),
            ]),
        ]),
    ])


def _teams_panel():
    return html.Div(id="panel-teams", className="panel", children=[
        html.Div(className="loader-grid", style={"gridTemplateColumns": "1fr"}, children=[
            html.Div(className="field-group", children=[
                _label("Team"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(
                        id="sel-team",
                        options=[{"label": team, "value": team}
                                 for team in TEAM_INFO.keys()],
                        value="Red Bull",
                        clearable=False,
                    ),
                ]),
            ]),
        ]),
        html.Div(className="stats-section", children=[
            html.Div(className="team-hero", children=[
                html.Div(id="team-name", className="stat-val"),
                html.Div(id="team-drivers", className="team-drivers"),
                html.Div(id="team-desc", className="team-description"),
            ]),
            html.Div(className="team-card-row", children=[
                html.Div(className="team-card", children=[
                    html.Div("Team Color", className="stat-label"),
                    html.Div(id="team-color-band", className="team-color-dot"),
                ]),
                html.Div(className="team-card", children=[
                    html.Div("Driver Lineup", className="stat-label"),
                    html.Div(id="team-lineup", className="team-lineup"),
                ]),
            ]),
            html.Div(className="team-stats-grid", children=[
                _stat_card("team-championships", "team-championships-sub", "Constructors' Titles"),
                _stat_card("team-drivers-championships", "team-drivers-championships-sub", "Drivers' Titles"),
                _stat_card("team-wins", "team-wins-sub", "Race Wins"),
                _stat_card("team-poles", "team-poles-sub", "Pole Positions"),
                _stat_card("team-founded", "team-founded-sub", "Founded"),
                _stat_card("team-base", "team-base-sub", "Base"),
            ]),
        ]),
    ])


def _replay_panel():
    """Race replay — canvas-based, zero Plotly roundtrips during animation."""
    return html.Div(id="panel-replay", className="panel", children=[

        # ── Main layout: canvas track + sidebar ─────────────────────────
        html.Div(className="replay-main", children=[

            # Canvas iframe (full renderer lives inside)
            html.Div(className="replay-track-container", style={"position": "relative"}, children=[
                html.Iframe(
                    id="replay-iframe",
                    src="/assets/replay_canvas.html",
                    style={
                        "width": "100%", "height": "560px",
                        "border": "none", "background": "transparent",
                        "display": "block",
                    },
                ),
                # HUD overlay (updated via postMessage listener below)
                html.Div(className="replay-hud", children=[
                    html.Div(className="replay-lap-badge", children=[
                        html.Span("LAP", className="replay-lap-label"),
                        html.Span("—", id="replay-lap-num",   className="replay-lap-val"),
                        html.Span("",  id="replay-lap-total", className="replay-lap-total"),
                    ]),
                    html.Div(className="replay-time-badge", children=[
                        html.Span("TIME", className="replay-time-label"),
                        html.Span("—", id="replay-time-val", className="replay-time-val"),
                    ]),
                ]),
            ]),

            # Sidebar leaderboard (updated by postMessage listener)
            html.Div(className="replay-sidebar", children=[
                html.Div(className="replay-leaderboard", children=[
                    html.Div("LIVE ORDER", className="replay-lb-header"),
                    html.Div(id="replay-leaderboard-body", children=[
                        html.Div(className="empty-state",
                                 children=["Load a session to start replay"]),
                    ]),
                ]),
            ]),
        ]),

        # ── Controls: just Play/Reset + legend ───────────────────────────
        html.Div(className="replay-controls-wrap", children=[
            html.Div(className="replay-controls", children=[
                html.Button("▶  PLAY", id="replay-play-btn",
                            className="load-btn replay-play", n_clicks=0),
                html.Button("■  RESET", id="replay-reset-btn",
                            className="outline-btn", n_clicks=0),
            ]),
            html.Div(id="replay-legend", className="replay-legend"),
        ]),

        # Hidden stores — keep same IDs so callbacks don't break
        dcc.Store(id="store-replay-data"),
        dcc.Store(id="store-replay-frame",   data=0),
        dcc.Store(id="store-replay-playing", data=False),
        # Interval kept (disabled) so existing callback refs don't error
        dcc.Interval(id="replay-interval", interval=500, disabled=True),
        # Dummy elements to satisfy any remaining callback outputs
        html.Div(id="replay-frame-slider", style={"display": "none"}),
    ])


def _calendar_panel():
    """2025 F1 season calendar — dynamic, updated via callback."""
    return html.Div(id="panel-calendar", className="panel", children=[
        # Hero
        html.Div(className="calendar-hero", children=[
            html.Div("2025 SEASON", id="calendar-hero-title",
                     className="calendar-hero-title"),
            html.Div("Formula 1 World Championship Calendar",
                     className="calendar-hero-sub"),
        ]),
        # Year selector
        html.Div(className="loader-grid",
                 style={"gridTemplateColumns": "200px", "marginBottom": "16px"},
                 children=[
            html.Div(className="field-group", children=[
                _label("Season"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(id="sel-calendar-year",
                                 options=[{"label": str(y), "value": y}
                                          for y in YEARS],
                                 value=2025, clearable=False, searchable=False),
                ]),
            ]),
        ]),
        # Upcoming
        html.Div(id="calendar-upcoming-label",
                 className="calendar-section-label"),
        html.Div(id="calendar-upcoming-grid", className="calendar-grid"),
        # Completed
        html.Div(id="calendar-completed-label",
                 className="calendar-section-label",
                 style={"marginTop": "32px"}),
        html.Div(id="calendar-completed-grid", className="calendar-grid"),
        # Hidden store
        dcc.Store(id="store-calendar-click"),
    ])


# ── Root layout ───────────────────────────────────────────────────────────────

def build_layout():
    return html.Div(className="dash", children=[

        dcc.Store(id="store-session",  storage_type="memory"),
        dcc.Store(id="store-tel-type", storage_type="memory", data="speed"),

        # ── Top bar ───────────────────────────────────────────────────────
        html.Div(className="topbar", children=[
            html.Div(className="topbar-left", children=[
                html.Div("F1", className="topbar-brand"),
                html.Div(className="session-pill", children=[
                    html.Div(className="live-dot", id="live-dot"),
                    html.Span("NO SESSION", id="session-type-label",
                              className="session-label"),
                ]),
                html.Span("Select a session to begin", id="gp-title-label",
                          className="gp-title"),
            ]),
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "24px"},
                     children=[
                html.Div(className="weather-badges", children=[
                    html.Span("— AIR", id="weather-air",   className="weather-pill"),
                    html.Span("— TRK", id="weather-track", className="weather-pill"),
                    html.Span("— m/s", id="weather-wind",  className="weather-pill"),
                ]),
                html.Div(style={"textAlign": "right"}, children=[
                    html.Div("LAP", className="lap-sub"),
                    html.Div("—/—", id="lap-display", className="lap-counter"),
                ]),
            ]),
        ]),

        # ── Navigation tabs ───────────────────────────────────────────────
        html.Div(className="nav-tabs", children=[
            html.Button("Session",     id="tab-session",   className="tab-btn active", n_clicks=0),
            html.Button("Race Order",  id="tab-standings", className="tab-btn",        n_clicks=0),
            html.Button("Track Map",   id="tab-track",     className="tab-btn",        n_clicks=0),
            html.Button("Telemetry",   id="tab-telemetry", className="tab-btn",        n_clicks=0),
            html.Button("Compare",     id="tab-compare",   className="tab-btn",        n_clicks=0),
            html.Button("Circuits",    id="tab-circuits",  className="tab-btn",        n_clicks=0),
            html.Button("Teams",       id="tab-teams",     className="tab-btn",        n_clicks=0),
            html.Button("Race Replay", id="tab-replay",    className="tab-btn",        n_clicks=0),
            html.Button("Calendar",    id="tab-calendar",  className="tab-btn",        n_clicks=0),
        ]),

        # ── Panels ────────────────────────────────────────────────────────
        html.Div(className="content", children=[
            _session_panel(),
            _standings_panel(),
            _track_panel(),
            _telemetry_panel(),
            _compare_panel(),
            _circuits_panel(),
            _teams_panel(),
            _replay_panel(),
            _calendar_panel(),
        ]),

        # ── Status bar ────────────────────────────────────────────────────
        html.Div(className="status-bar", children=[
            html.Div(className="status-dot idle", id="status-dot"),
            html.Span("IDLE — NO SESSION LOADED", id="status-text",
                      className="status-text"),
            html.Div(style={"flex": "1"}),
            html.Div(className="mini-sectors", children=[
                html.Div(className="mini-sec p"),
                html.Div(className="mini-sec f"),
                html.Div(className="mini-sec y"),
            ]),
            html.Span("POWERED BY FASTF1", className="status-text",
                      style={"marginLeft": "6px"}),
        ]),
    ])