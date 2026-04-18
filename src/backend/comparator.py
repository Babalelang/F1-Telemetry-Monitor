# comparator.py — align two drivers' telemetry for head-to-head
def compare_drivers(session, driver1, driver2):
    lap1 = session.laps.pick_driver(driver1).pick_fastest()
    lap2 = session.laps.pick_driver(driver2).pick_fastest()

    tel1 = lap1.get_car_data().add_distance()
    tel2 = lap2.get_car_data().add_distance()

    return tel1, tel2, lap1, lap2