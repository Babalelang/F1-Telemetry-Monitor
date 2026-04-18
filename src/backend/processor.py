#this code does lap filtering and compound 
#so it has two functions

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
