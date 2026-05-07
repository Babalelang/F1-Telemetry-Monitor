# config.py — F1 Telemetry Dashboard Configuration

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

current_year = datetime.now().year
Valid_Years = list(range(2018, current_year + 1))
year = list(range(2018, current_year + 1))

SESSION_TYPES  = ["R", "Q", "FP1", "FP2", "FP3", "S"]
SESSION_LABELS = {"R": "Race", "Q": "Qualifying", "FP1": "FP1",
                  "FP2": "FP2", "FP3": "FP3", "S": "Sprint"}

