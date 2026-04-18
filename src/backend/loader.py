#loader.py
#this code touches anything that touches fastf1 directly

import fastf1
import numpy as np

fastf1.Cache.enable_cache('./cache')

#defining and loading the session
def load_session(year,gp,session_type):
    session = fastf1.get_session(year,gp,session_type)
    session.load()
    return session

def get_telemetry(lap):
    return lap.get_car_data().add_distance()



#Weather data
def get_weather(session):
    return session.weather_data
