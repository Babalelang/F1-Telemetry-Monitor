#main py this code should only does user input and orchestrates other files

from config import GRP_MAP, session_types, Valid_Years
from loader import load_session, get_telemetry
from processor import get_driver_lap, get_compound_summary

#year
user_year = int(input("Enter Year: "))
if user_year not in Valid_Years:
    raise ValueError("Year not found in telemetry")

#Grand Prix
user_input = input("Enter Grand Prix Name: ").lower().strip()
if user_input not in GRP_MAP:
   raise ValueError("Invalid Grand Prix")
gp = GRP_MAP[user_input]

#session type
user_session = input("Enter session type (FP1, FP2, FP3, Q, S, SS, R): ").upper()
if user_session not in session_types:
    raise ValueError("Invalid session type")
    
#loading session based of user input
session = load_session(user_year,gp,user_session)

#driver
drivers = session.laps['Driver'].unique()
print("Available drivers:", drivers)
user_driver = input("Enter driver code (e.g. VER, HAM): ").upper()
if user_driver not in drivers:
    raise ValueError("Driver not in this session")

#Lap
lap_choice = input("Fastest lap or specific lap number? (f / number): ").strip().lower()
lap = get_driver_lap(session, user_driver, lap_choice)

#Compound Summary
summary = get_compound_summary(session.laps)
for compound, count in summary.items():
    print(f"{compound} laps: {count}")

# Telemetry
# i think it includes x,y,z positions
telemetry = get_telemetry(lap)
print(telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear', 'DRS']].head())