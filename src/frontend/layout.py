from dash import dcc, html
from datetime import datetime

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

# Dynamic — always includes current year (covers 2026 and beyond automatically)
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

CIRCUIT_INFO = {
    "bahrain": {
        "name": "Bahrain Grand Prix",
        "location": "Sakhir",
        "length": "5.412 km",
        "corners": "15",
        "first_gp": "2004",
        "races": "19",
        "lap_record": "1:31.447",
        "record_holder": "Pedro de la Rosa (2005)",
        "description": "The Bahrain International Circuit hosts the season opener with its high-speed corners and desert location.",
    },
    "saudi_arabia": {
        "name": "Saudi Arabian Grand Prix",
        "location": "Jeddah",
        "length": "6.174 km",
        "corners": "27",
        "first_gp": "2021",
        "races": "3",
        "lap_record": "1:30.734",
        "record_holder": "Lewis Hamilton (2021)",
        "description": "A street circuit in Jeddah featuring the fastest corner in F1 history at over 320 km/h.",
    },
    "australia": {
        "name": "Australian Grand Prix",
        "location": "Melbourne",
        "length": "5.278 km",
        "corners": "16",
        "first_gp": "1996",
        "races": "25",
        "lap_record": "1:24.125",
        "record_holder": "Michael Schumacher (2004)",
        "description": "Albert Park's scenic circuit combines street and permanent sections with challenging weather.",
    },
    "japan": {
        "name": "Japanese Grand Prix",
        "location": "Suzuka",
        "length": "5.807 km",
        "corners": "18",
        "first_gp": "1987",
        "races": "30",
        "lap_record": "1:30.983",
        "record_holder": "Lewis Hamilton (2019)",
        "description": "The iconic figure-8 layout at Suzuka is known for its technical challenges and fan passion.",
    },
    "china": {
        "name": "Chinese Grand Prix",
        "location": "Shanghai",
        "length": "5.451 km",
        "corners": "16",
        "first_gp": "2004",
        "races": "16",
        "lap_record": "1:32.238",
        "record_holder": "Michael Schumacher (2004)",
        "description": "Shanghai International Circuit features long straights and heavy braking zones.",
    },
    "miami": {
        "name": "Miami Grand Prix",
        "location": "Miami Gardens",
        "length": "5.412 km",
        "corners": "19",
        "first_gp": "2022",
        "races": "2",
        "lap_record": "1:29.708",
        "record_holder": "Max Verstappen (2023)",
        "description": "A street circuit around Hard Rock Stadium, bringing F1 to the heart of Miami.",
    },
    "imola": {
        "name": "Emilia Romagna Grand Prix",
        "location": "Imola",
        "length": "4.909 km",
        "corners": "19",
        "first_gp": "1980",
        "races": "28",
        "lap_record": "1:15.484",
        "record_holder": "Lewis Hamilton (2020)",
        "description": "The historic Autodromo Enzo e Dino Ferrari with its high-speed corners and chicanes.",
    },
    "monaco": {
        "name": "Monaco Grand Prix",
        "location": "Monte Carlo",
        "length": "3.337 km",
        "corners": "19",
        "first_gp": "1950",
        "races": "69",
        "lap_record": "1:10.166",
        "record_holder": "Lewis Hamilton (2021)",
        "description": "The most prestigious race on the narrow streets of Monaco, requiring precision driving.",
    },
    "spain": {
        "name": "Spanish Grand Prix",
        "location": "Barcelona",
        "length": "4.675 km",
        "corners": "16",
        "first_gp": "1991",
        "races": "30",
        "lap_record": "1:12.272",
        "record_holder": "Max Verstappen (2021)",
        "description": "Circuit de Barcelona-Catalunya is a testing ground for car development with varied corners.",
    },
    "canada": {
        "name": "Canadian Grand Prix",
        "location": "Montreal",
        "length": "4.361 km",
        "corners": "14",
        "first_gp": "1978",
        "races": "42",
        "lap_record": "1:13.078",
        "record_holder": "Valtteri Bottas (2019)",
        "description": "The Circuit Gilles Villeneuve features the famous Wall of Champions and heavy braking.",
    },
    "austria": {
        "name": "Austrian Grand Prix",
        "location": "Spielberg",
        "length": "4.318 km",
        "corners": "10",
        "first_gp": "1970",
        "races": "34",
        "lap_record": "1:05.619",
        "record_holder": "Carlos Sainz (2020)",
        "description": "Red Bull Ring's high-altitude location provides unique downforce challenges.",
    },
    "britain": {
        "name": "British Grand Prix",
        "location": "Silverstone",
        "length": "5.891 km",
        "corners": "18",
        "first_gp": "1950",
        "races": "71",
        "lap_record": "1:27.097",
        "record_holder": "Max Verstappen (2020)",
        "description": "The historic Silverstone circuit is the home of British motorsport with fast corners.",
    },
    "hungary": {
        "name": "Hungarian Grand Prix",
        "location": "Budapest",
        "length": "4.381 km",
        "corners": "14",
        "first_gp": "1986",
        "races": "37",
        "lap_record": "1:16.627",
        "record_holder": "Lewis Hamilton (2020)",
        "description": "Hungaroring's tight layout makes overtaking difficult and strategy crucial.",
    },
    "belgium": {
        "name": "Belgian Grand Prix",
        "location": "Spa-Francorchamps",
        "length": "7.004 km",
        "corners": "19",
        "first_gp": "1950",
        "races": "66",
        "lap_record": "1:46.286",
        "record_holder": "Valtteri Bottas (2018)",
        "description": "The longest circuit with the famous Eau Rouge corner and unpredictable weather.",
    },
    "netherlands": {
        "name": "Dutch Grand Prix",
        "location": "Zandvoort",
        "length": "4.259 km",
        "corners": "14",
        "first_gp": "1952",
        "races": "33",
        "lap_record": "1:11.097",
        "record_holder": "Lewis Hamilton (2021)",
        "description": "The sandy dunes circuit returned in 2021 with high-speed corners and banking.",
    },
    "italy": {
        "name": "Italian Grand Prix",
        "location": "Monza",
        "length": "5.793 km",
        "corners": "11",
        "first_gp": "1950",
        "races": "73",
        "lap_record": "1:21.046",
        "record_holder": "Rubens Barrichello (2004)",
        "description": "Monza's high-speed temple of speed with minimal downforce required.",
    },
    "azerbaijan": {
        "name": "Azerbaijan Grand Prix",
        "location": "Baku",
        "length": "6.003 km",
        "corners": "20",
        "first_gp": "2016",
        "races": "6",
        "lap_record": "1:43.009",
        "record_holder": "Charles Leclerc (2019)",
        "description": "Baku City Circuit combines street and permanent sections with the fastest corner in F1.",
    },
    "singapore": {
        "name": "Singapore Grand Prix",
        "location": "Marina Bay",
        "length": "5.063 km",
        "corners": "23",
        "first_gp": "2008",
        "races": "14",
        "lap_record": "1:41.905",
        "record_holder": "Kevin Magnussen (2018)",
        "description": "The night race through the streets of Singapore with its tight, twisty layout.",
    },
    "usa": {
        "name": "United States Grand Prix",
        "location": "Austin",
        "length": "5.513 km",
        "corners": "20",
        "first_gp": "2012",
        "races": "10",
        "lap_record": "1:36.169",
        "record_holder": "Charles Leclerc (2019)",
        "description": "Circuit of the Americas features the challenging Esses and high-speed corners.",
    },
    "mexico": {
        "name": "Mexico City Grand Prix",
        "location": "Mexico City",
        "length": "4.304 km",
        "corners": "17",
        "first_gp": "1963",
        "races": "22",
        "lap_record": "1:17.774",
        "record_holder": "Valtteri Bottas (2018)",
        "description": "Autódromo Hermanos Rodríguez at high altitude requires careful engine management.",
    },
    "brazil": {
        "name": "São Paulo Grand Prix",
        "location": "São Paulo",
        "length": "4.309 km",
        "corners": "15",
        "first_gp": "1973",
        "races": "39",
        "lap_record": "1:10.540",
        "record_holder": "Valtteri Bottas (2018)",
        "description": "Interlagos circuit with its downhill start and challenging corners.",
    },
    "las_vegas": {
        "name": "Las Vegas Grand Prix",
        "location": "Las Vegas",
        "length": "6.201 km",
        "corners": "17",
        "first_gp": "2023",
        "races": "1",
        "lap_record": "1:35.490",
        "record_holder": "Oscar Piastri (2023)",
        "description": "The Strip circuit brings F1 to the neon lights of Las Vegas with long straights.",
    },
    "qatar": {
        "name": "Qatar Grand Prix",
        "location": "Lusail",
        "length": "5.419 km",
        "corners": "16",
        "first_gp": "2021",
        "races": "3",
        "lap_record": "1:23.196",
        "record_holder": "Max Verstappen (2023)",
        "description": "Lusail International Circuit hosts the night race with smooth, flowing corners.",
    },
    "abu_dhabi": {
        "name": "Abu Dhabi Grand Prix",
        "location": "Yas Island",
        "length": "5.281 km",
        "corners": "21",
        "first_gp": "2009",
        "races": "14",
        "lap_record": "1:26.103",
        "record_holder": "Max Verstappen (2021)",
        "description": "Yas Marina Circuit's season finale with the famous hotel backdrop and yacht marina.",
    },
}

TEAM_INFO = {
    "Red Bull": {
        "color": "#3671C6",
        "drivers": ["VER", "PER"],
        "description": "A championship-contending team with a balanced package and strong race pace.",
        "championships": "6 Constructors' Championships",
        "drivers_championships": "8 Drivers' Championships",
        "wins": "115",
        "poles": "103",
        "founded": "2005",
        "base": "Milton Keynes, UK",
    },
    "Mercedes": {
        "color": "#27F4D2",
        "drivers": ["HAM", "RUS"],
        "description": "A hybrid-era powerhouse known for strategic strength and reliability.",
        "championships": "8 Constructors' Championships",
        "drivers_championships": "8 Drivers' Championships",
        "wins": "125",
        "poles": "137",
        "founded": "2010",
        "base": "Brackley, UK",
    },
    "Ferrari": {
        "color": "#E8002D",
        "drivers": ["LEC", "SAI"],
        "description": "Iconic Italian team with passionate fans and aggressive racecraft.",
        "championships": "16 Constructors' Championships",
        "drivers_championships": "15 Drivers' Championships",
        "wins": "243",
        "poles": "252",
        "founded": "1929",
        "base": "Maranello, Italy",
    },
    "McLaren": {
        "color": "#FF8000",
        "drivers": ["NOR", "PIA"],
        "description": "British squad with a focus on development and consistent podium finishes.",
        "championships": "8 Constructors' Championships",
        "drivers_championships": "12 Drivers' Championships",
        "wins": "183",
        "poles": "156",
        "founded": "1963",
        "base": "Woking, UK",
    },
    "Aston Martin": {
        "color": "#358C75",
        "drivers": ["ALO", "STR"],
        "description": "A team blending experience and innovation for strong midfield performance.",
        "championships": "0 Constructors' Championships",
        "drivers_championships": "0 Drivers' Championships",
        "wins": "0",
        "poles": "1",
        "founded": "2021",
        "base": "Silverstone, UK",
    },
    "Alpine": {
        "color": "#FF87BC",
        "drivers": ["OCO", "GAS"],
        "description": "French team focused on qualifying pace and technical upgrades.",
        "championships": "2 Constructors' Championships",
        "drivers_championships": "2 Drivers' Championships",
        "wins": "21",
        "poles": "20",
        "founded": "2021",
        "base": "Enstone, UK",
    },
    "Williams": {
        "color": "#64C4FF",
        "drivers": ["ALB", "SAR"],
        "description": "A historic team rebuilding with young talent and renewed ambition.",
        "championships": "9 Constructors' Championships",
        "drivers_championships": "7 Drivers' Championships",
        "wins": "114",
        "poles": "128",
        "founded": "1977",
        "base": "Grove, UK",
    },
    "AlphaTauri": {
        "color": "#5E8FAA",
        "drivers": ["TSU", "LAW"],
        "description": "Junior team with strong driver development and occasional surprises.",
        "championships": "0 Constructors' Championships",
        "drivers_championships": "0 Drivers' Championships",
        "wins": "1",
        "poles": "1",
        "founded": "2020",
        "base": "Faenza, Italy",
    },
    "Haas": {
        "color": "#B6BABD",
        "drivers": ["HUL", "MAG", "BOR"],
        "description": "A compact team that maximizes opportunities with efficient engineering.",
        "championships": "0 Constructors' Championships",
        "drivers_championships": "0 Drivers' Championships",
        "wins": "0",
        "poles": "0",
        "founded": "2016",
        "base": "Kannapolis, USA",
    },
    "Alfa Romeo": {
        "color": "#00E701",
        "drivers": ["BOT", "ZHO"],
        "description": "Experienced outfit blending veteran stability with fresh talent.",
        "championships": "0 Constructors' Championships",
        "drivers_championships": "0 Drivers' Championships",
        "wins": "1",
        "poles": "1",
        "founded": "2019",
        "base": "Hinwil, Switzerland",
    },
}


def _driver_options():
    return [{"label": d, "value": d,
             "title": TEAM_COLORS.get(d, "#888888")} for d in DRIVERS]


def _label(text):
    return html.Div(text, className="field-label")


def _stat_card(val_id, sub_id, label):
    return html.Div([
        html.Div(label,  className="stat-label"),
        html.Div("—",    id=val_id, className="stat-val"),
        html.Div("—",    id=sub_id, className="stat-sub"),
    ], className="stat-card")


# ── Panels ────────────────────────────────────────────────────────────────────

def _session_panel():
    drv_opts = _driver_options()
    return html.Div(id="panel-session", className="panel active", children=[

        html.Div(className="loader-grid", children=[
            html.Div(className="field-group", children=[
                _label("Year"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(
                        id="sel-year",
                        options=[{"label": str(y), "value": y} for y in YEARS],
                        value=_CURRENT_YEAR,
                        clearable=False,
                        searchable=False,
                    ),
                ]),
            ]),
            html.Div(className="field-group", children=[
                _label("Grand Prix"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(
                        id="sel-gp",
                        options=[{"label": v, "value": k} for k, v in GRP_MAP.items()],
                        value="japan",
                        clearable=False,
                    ),
                ]),
            ]),
            html.Div(className="field-group", children=[
                _label("Session"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(
                        id="sel-session",
                        options=[{"label": SESSION_LABELS[s], "value": s}
                                 for s in SESSION_TYPES],
                        value="R",
                        clearable=False,
                        searchable=False,
                    ),
                ]),
            ]),
        ]),

        html.Div(className="loader-row", children=[
            html.Div(style={"flex": "1"}),
            html.Button("Load Session", id="load-btn",
                        className="load-btn", n_clicks=0),
        ]),

        dcc.Loading(id="loading-session", type="circle", color="#E8002D",
                    children=html.Div(id="load-trigger", style={"display": "none"})),

        html.Div(style={"marginTop": "18px"}, children=[
            _label("Quick Plots"),
            html.Div(id="plot-btns", className="btn-row disabled-plots",
                     style={"marginTop": "10px"}, children=[
                html.Button("Speed Trace",    id="btn-speed-trace",
                            className="outline-btn", n_clicks=0),
                html.Button("Full Telemetry", id="btn-tel-panel",
                            className="outline-btn", n_clicks=0),
                html.Button("Lap Times",      id="btn-lap-times",
                            className="outline-btn", n_clicks=0),
                html.Button("Track Map",      id="btn-track-map",
                            className="outline-btn", n_clicks=0),
                html.Button("Tyre Usage",     id="btn-compounds",
                            className="outline-btn", n_clicks=0),
            ]),
        ]),

        html.Div(className="stats-section", children=[
            _label("Session Stats"),
            html.Div(className="stats-grid", style={"marginTop": "12px"}, children=[
                _stat_card("stat-best",  "stat-best-drv",  "Best Lap"),
                _stat_card("stat-avg",   "stat-avg-sub",   "Avg Lap"),
                _stat_card("stat-cons",  "stat-cons-sub",  "Consistency"),
                _stat_card("stat-worst", "stat-worst-sub", "Worst Lap"),
            ]),
        ]),
    ])


def _standings_panel():
    return html.Div(id="panel-standings", className="panel", children=[
        html.Div(className="standings-wrap", children=[
            html.Div(className="standings-header", children=[
                html.Span(c, className="sh-cell")
                for c in ["P", "DRV", "Name", "Tyre", "Gap", "Last", "Best"]
            ]),
            html.Div(id="standings-body", className="scroll-region", children=[
                html.Div(className="empty-state", children=[
                    html.Div("🏁", className="icon"),
                    "Load a session to see race order",
                ]),
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
                    style={"height": "340px", "width": "100%"},
                ),
            ]),
            html.Div(className="track-side", children=[
                html.Div(className="stat-card", children=[
                    html.Div("Circuit",       className="stat-label"),
                    html.Div("—", id="circuit-name", className="stat-val",
                             style={"fontSize": "14px"}),
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
        html.Div(className="loader-grid", children=[
            html.Div(className="field-group", children=[
                _label("Driver"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(id="sel-tel-driver", options=[], value=None,
                                 clearable=False, placeholder="Select driver"),
                ]),
            ]),
        ]),
        html.Div(className="chart-wrap", children=[
            html.Div("Speed Trace — Load a session first",
                     id="tel-chart-title", className="chart-title"),
            dcc.Graph(id="tel-graph", config={"displayModeBar": False},
                      style={"height": "220px"}),
        ]),
        html.Div(className="btn-row", style={"marginTop": "10px"}, children=[
            html.Button("Speed",    id="btn-tel-speed",
                        className="outline-btn active", n_clicks=0),
            html.Button("Throttle", id="btn-tel-throttle",
                        className="outline-btn", n_clicks=0),
            html.Button("Brake",    id="btn-tel-brake",
                        className="outline-btn", n_clicks=0),
            html.Button("Gear",     id="btn-tel-gear",
                        className="outline-btn", n_clicks=0),
        ]),
    ])


def _compare_panel():
    drv_opts = _driver_options()

    def _card(dot_id, name_id, lap_id, s1_id, s2_id, s3_id):
        return html.Div(className="driver-select-card", children=[
            html.Div(className="ds-header", children=[
                html.Div(id=dot_id, className="driver-dot",
                         style={"width": "10px", "height": "10px",
                                "borderRadius": "50%", "background": "#888888",
                                "flexShrink": "0"}),
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
        html.Div(className="loader-row", style={"marginBottom": "18px"}, children=[
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
        html.Div(className="chart-wrap", style={"height": "220px"}, children=[
            html.Div("Speed Overlay — Driver 1 vs Driver 2", className="chart-title"),
            dcc.Graph(id="cmp-graph", config={"displayModeBar": False},
                      style={"height": "170px"}),
        ]),
    ])


def _circuits_panel():
    return html.Div(id="panel-circuits", className="panel", children=[
        html.Div(className="loader-grid", children=[
            html.Div(className="field-group", children=[
                _label("Circuit"),
                html.Div(className="f1-dropdown", children=[
                    dcc.Dropdown(
                        id="sel-circuit",
                        options=[{"label": data["name"], "value": key}
                                 for key, data in CIRCUIT_INFO.items()],
                        value="japan",
                        clearable=False,
                    ),
                ]),
            ]),
        ]),
        html.Div(className="stats-section", children=[
            html.Div("Circuit Details", className="chart-title"),
            html.Div(className="stats-grid", style={"marginTop": "12px"}, children=[
                _stat_card("circuit-length", "circuit-length-sub", "Length"),
                _stat_card("circuit-corners", "circuit-corners-sub", "Corners"),
                _stat_card("circuit-firstgp", "circuit-firstgp-sub", "First GP"),
                _stat_card("circuit-races", "circuit-races-sub", "Races"),
            ]),
            html.Div(className="stats-grid", style={"marginTop": "12px"}, children=[
                _stat_card("circuit-best-lap", "circuit-best-driver", "Best Lap"),
                _stat_card("circuit-lap-record", "circuit-record-holder", "Lap Record"),
                html.Div(className="circuit-description", id="circuit-description",
                         style={"gridColumn": "1 / -1", "fontSize": "13px", "color": "rgba(255,255,255,0.72)", "paddingTop": "8px"}),
            ]),
        ]),
    ])


def _teams_panel():
    return html.Div(id="panel-teams", className="panel", children=[
        html.Div(className="loader-grid", children=[
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
    return html.Div(id="panel-replay", className="panel", children=[

        html.Div(className="replay-wrap", children=[
            dcc.Graph(
                id="replay-graph",
                config={"displayModeBar": False, "staticPlot": False},
                style={"height": "460px"},
            ),
            html.Div(className="replay-hud", children=[
                html.Div(className="replay-lap-badge", children=[
                    html.Span("LAP", className="replay-lap-label"),
                    html.Span("—", id="replay-lap-num",   className="replay-lap-val"),
                    html.Span("",  id="replay-lap-total", className="replay-lap-total"),
                ]),
            ]),
        ]),

        html.Div(className="replay-controls", children=[
            html.Button("▶  Play", id="replay-play-btn",
                        className="load-btn replay-play", n_clicks=0),
            html.Button("⏹ Reset", id="replay-reset-btn",
                        className="outline-btn", n_clicks=0),
            html.Div(className="replay-scrub", children=[
                _label("Frame"),
                dcc.Slider(id="replay-frame-slider", min=0, max=100,
                           step=1, value=0, marks={},
                           tooltip={"always_visible": False},
                           className="replay-slider"),
            ]),
        ]),

        html.Div(id="replay-legend", className="replay-legend"),

        dcc.Store(id="store-replay-data"),
        dcc.Store(id="store-replay-frame",   data=0),
        dcc.Store(id="store-replay-playing", data=False),
        dcc.Interval(id="replay-interval",   interval=150, disabled=True),
    ])


# ── Root layout ───────────────────────────────────────────────────────────────
def build_layout():
    return html.Div(className="dash", children=[

        dcc.Store(id="store-session",  storage_type="memory"),
        dcc.Store(id="store-tel-type", storage_type="memory", data="speed"),

        # Top bar
        html.Div(className="topbar", children=[
            html.Div(className="topbar-left", children=[
                html.Div(className="session-pill", children=[
                    html.Div(className="live-dot"),
                    html.Span("NO SESSION", id="session-type-label",
                              className="session-label"),
                ]),
                html.Span("Select a session to begin", id="gp-title-label",
                          className="gp-title"),
            ]),
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "20px"},
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

        # Tabs
        html.Div(className="nav-tabs", children=[
            html.Button("Session",     id="tab-session",   className="tab-btn active", n_clicks=0),
            html.Button("Race Order",  id="tab-standings", className="tab-btn",        n_clicks=0),
            html.Button("Track Map",   id="tab-track",     className="tab-btn",        n_clicks=0),
            html.Button("Telemetry",   id="tab-telemetry", className="tab-btn",        n_clicks=0),
            html.Button("Compare",     id="tab-compare",   className="tab-btn",        n_clicks=0),
            html.Button("Circuits",    id="tab-circuits",  className="tab-btn",        n_clicks=0),
            html.Button("Teams",       id="tab-teams",     className="tab-btn",        n_clicks=0),
            html.Button("Race Replay", id="tab-replay",    className="tab-btn",        n_clicks=0),
        ]),

        # Panels
        html.Div(className="content", children=[
            _session_panel(),
            _standings_panel(),
            _track_panel(),
            _telemetry_panel(),
            _compare_panel(),
            _circuits_panel(),
            _teams_panel(),
            _replay_panel(),
        ]),

        # Status bar
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