#this code touches anything that touches fastf1 directly

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

fastf1.Cache.enable_cache('./cache')

#defining and loading the session
def load_session(year,gp,session_type):
    session = fastf1.get_session(year,gp,session_type)
    session.load()
    return session

def get_telemetry(lap):
    return lap.get_car_data().add_distance()

#getting postion data (GPS, X,Y,Z coordinates)
#x = get_telemetry['X'] - get telemetry is a function not data dummy
#y = get_telemetry['Y']

def plot_position(lap, driver):
    tel = get_telemetry(lap)
    x = tel['X']
    y = tel['Y']

    plt.figure(figsize=(10,6))
    plt.plot(x,y,label =f'{driver}Position ')
    plt.title(f'Position Data - {driver} ')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.show()

#Weather data
def get_weather(session):
    return session.weather_data
