#config.py

from datetime import datetime

#this is me trying to load the sessions
#so we need mapping layering
GRP_MAP = {
    "bahrain": "Bahrain Grand Prix",
    "saudi arabia": "Saudi Arabian Grand Prix",
    "australia": "Australian Grand Prix",
    "japan": "Japanese Grand Prix",
    "china": "Chinese Grand Prix",
    "miami": "Miami Grand Prix",
    "imola": "Emilia Romagna Grand Prix",
    "monaco": "Monaco Grand Prix",
    "spain": "Spanish Grand Prix",
    "canada": "Canadian Grand Prix",
    "austria": "Austrian Grand Prix",
    "britain": "British Grand Prix",
    "hungary": "Hungarian Grand Prix",
    "belgium": "Belgian Grand Prix",
    "netherlands": "Dutch Grand Prix",
    "italy": "Italian Grand Prix",
    "azerbaijan": "Azerbaijan Grand Prix",
    "singapore": "Singapore Grand Prix",
    "usa": "United States Grand Prix",
    "mexico": "Mexico City Grand Prix",
    "brazil": "São Paulo Grand Prix",
    "las_vegas": "Las Vegas Grand Prix",
    "qatar": "Qatar Grand Prix",
    "abu_dhabi": "Abu Dhabi Grand Prix"
}
# for year we don't want a dictionary for year we just a range
#year =list(range(1950,2026)) - we could do this but i made it more dynamic

current_year = datetime.now().year
#Valid Years
Valid_Years = list(range(2018,current_year+1)) 
year = list(range(2018,current_year + 1))

session_types = ["FP1", "FP2", "FP3", "Q", "S", "SS", "R"]