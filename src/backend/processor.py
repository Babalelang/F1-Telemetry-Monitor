#processor.py this code does lap filtering and compound 
#so it has two functions
import numpy as np

#this function finds an specific lap for a driver
def get_driver_lap(session,driver,lap_choice): 
    driver_laps = session.laps.pick_driver(driver)
    if lap_choice == "f":
        return driver_laps.pick_fastest()
    else:
        filtered = driver_laps[driver_laps["LapNumber"]==int(lap_choice)]
        if filtered.empty:
            raise ValueError("Lap number not found")
        return filtered.iloc[0]

 #we are counting how many laps were done on each tyre type   
def get_compound_summary(laps):
    compounds = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
    summary = {}
    for c in compounds: 
        #we are filtering laps by tyres, counting them and storing the results in the empty summary result box
        summary[c] = len(laps.pick_compounds(c))
    return summary 
    
#lap time analysis
def lap_time_analysis(session,driver):
    laps = session.laps.pick_driver(driver)

    #convert the lap times to seconds
    lap_times = laps["LapTime"].dt.total_seconds()
    best_lap = lap_times.min()
    avg_laps =lap_times.mean()
    consistency =  lap_times.std()
    worst_lap =lap_times.max()

    return{
        "best_lap": best_lap,
        "average_lap":avg_laps,
        "consistency_std":consistency,
        "worst_lap": worst_lap
    }

#Sector analysis

#lap time analysis
def sector_time_analysis(session,driver):
    laps = session.laps.pick_driver(driver)
    return{
        "sector1_avg": laps["Sector1Time"].mean(),
        "sector2_avg": laps["Sector2Time"].mean(),
        "sector3_avg": laps["Sector3Time"].mean()
    }

#Driver comparision
def get_fastest_lap(session,driver):
    laps = session.laps.pick_driver(driver)
    return laps.pick_fastest()

def compare_telemetry(lap1,lap2):
    t1 = lap1.get_car_data().add_distance()
    t2 = lap2.get_car_data().add_distance()

    return t1,t2


def tyre_stint_analysis(session,driver):
    laps = session.laps.pick_driver(driver)

    stints = laps.groupby(["Stint", "Compound"])["TyreLife"].max()
    return stints

#Mini sectors / speed zones
def speed_zones(lap):
    telemetry = lap.get_car_data().add_distance()

    braking = telemetry[telemetry["Brake"] > 0]
    full_throttle = telemetry[telemetry["Throttle"] > 90]
    cornering = telemetry[(telemetry["Speed"] < 120) & (telemetry["Brake"] == False)]

    return {
        "braking_points": len(braking),
        "high_speed_zones": len(full_throttle),
        "cornering_zones": len(cornering)
    }