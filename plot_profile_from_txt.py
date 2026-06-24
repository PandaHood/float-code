import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from typing import List

def read_data(file_path):
    times = []
    depths = []
    
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(" ")
            timestamp_str = parts[1]
            depth = float(parts[5])
            
            timestamp = datetime.fromisoformat(timestamp_str)
            times.append(timestamp)
            depths.append(depth)
    
    return times, depths

def plot_depth_over_time(times: List[datetime], depths):
    plt.figure(figsize=(10, 6))
    plt.plot(times, depths, marker='o', color='black', linestyle='-', markersize=3)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.SecondLocator(interval=5))
    labels = plt.gca().get_xticklabels()
    for i, label in enumerate(labels):
        if i % 3 != 0:
            label.set_visible(False)
    plt.xlabel('Time (UTC)')
    plt.ylabel('Depth (m)')
    plt.title('Depth over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    file_path = "testing_seagrant/profile.txt"
    times, depths = read_data(file_path)
    plot_depth_over_time(times, depths)

if __name__ == "__main__":
    main()
