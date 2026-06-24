import csv
import matplotlib.pyplot as plt

LOG_FILE_PATH = "depth_log.csv"

times = []
depths = []

with open(LOG_FILE_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        times.append(i * 5)
        depths.append(float(row["Depth (m)"]))

plt.figure(figsize=(10, 6))
plt.plot(times, depths)
plt.xlabel("Time (s)")
plt.ylabel("Depth (m)")
plt.title("Float Depth Profile")
plt.gca().invert_yaxis()
plt.grid(True)
plt.tight_layout()
plt.savefig("depth_profile.png")
plt.show()
