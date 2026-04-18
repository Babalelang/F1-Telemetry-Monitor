# plotter.py
# All visualization lives here. Nothing else should call matplotlib directly.

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.collections import LineCollection
import numpy as np
import fastf1.plotting

fastf1.plotting.setup_mpl()

# 1. Speed Trace — single driver across a lap

def plot_speed_trace(telemetry, driver):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(telemetry["Distance"], telemetry["Speed"], color="red", linewidth=1.5)
    ax.set_title(f"Speed Trace — {driver}")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


# 2. Full Telemetry Panel — Speed, Throttle, Brake, Gear

def plot_telemetry_panel(telemetry, driver):
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f"Telemetry Panel — {driver}", fontsize=14)

    axes[0].plot(telemetry["Distance"], telemetry["Speed"], color="cyan", linewidth=1.2)
    axes[0].set_ylabel("Speed (km/h)")

    axes[1].plot(telemetry["Distance"], telemetry["Throttle"], color="green", linewidth=1.2)
    axes[1].set_ylabel("Throttle (%)")

    axes[2].plot(telemetry["Distance"], telemetry["Brake"], color="red", linewidth=1.2)
    axes[2].set_ylabel("Brake")

    axes[3].plot(telemetry["Distance"], telemetry["nGear"], color="orange", linewidth=1.2)
    axes[3].set_ylabel("Gear")
    axes[3].set_xlabel("Distance (m)")

    for ax in axes:
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# 3. Driver Comparison — speed overlay

def plot_speed_comparison(t1, t2, driver1, driver2):
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(t1["Distance"], t1["Speed"], label=driver1, linewidth=1.5)
    ax.plot(t2["Distance"], t2["Speed"], label=driver2, linewidth=1.5, linestyle="--")
    ax.set_title(f"Speed Comparison — {driver1} vs {driver2}")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 4. Track Map — X/Y position colored by speed

def plot_track_map(lap, driver):
    tel = lap.get_pos_data().add_distance()
    car = lap.get_car_data().add_distance()

    # Merge on distance so we can color by speed
    tel = tel.merge_channels(car)

    x = tel["X"].values
    y = tel["Y"].values
    speed = tel["Speed"].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(speed.min(), speed.max())
    lc = LineCollection(segments, cmap="plasma", norm=norm, linewidth=2)
    lc.set_array(speed)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.add_collection(lc)
    ax.autoscale()
    ax.set_aspect("equal")
    ax.axis("off")
    fig.colorbar(lc, ax=ax, label="Speed (km/h)")
    ax.set_title(f"Track Map — {driver} (colored by speed)")
    plt.tight_layout()
    plt.show()


# 5. Lap Time Chart — all laps for a driver

def plot_lap_times(session, driver):
    laps = session.laps.pick_drivers(driver).copy()
    laps["LapTimeSec"] = laps["LapTime"].dt.total_seconds()
    laps = laps.dropna(subset=["LapTimeSec"])

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(laps["LapNumber"], laps["LapTimeSec"], color="red", s=30)
    ax.set_title(f"Lap Times — {driver}")
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time (s)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 6. Compound Bar Chart — tyre usage across session

def plot_compound_summary(summary):
    compounds = list(summary.keys())
    counts = list(summary.values())
    colors = {
        "SOFT": "red",
        "MEDIUM": "yellow",
        "HARD": "white",
        "INTERMEDIATE": "green",
        "WET": "blue"
    }
    bar_colors = [colors.get(c, "gray") for c in compounds]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(compounds, counts, color=bar_colors, edgecolor="black")
    ax.set_title("Tyre Compound Usage")
    ax.set_xlabel("Compound")
    ax.set_ylabel("Laps")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()