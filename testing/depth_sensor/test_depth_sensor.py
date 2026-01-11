from src.depth_sensor import *

import time

def read_depth(sensor):
    # Trigger a new I2C read; returns True on success
    if not sensor.read():
        return None, None
    # You can either use sensor.depth() (which applies default density)
    # or compute depth from an adjusted pressure:
    return sensor.depth(), sensor.pressure()

if __name__ == "__main__":
    num_read = 5
    # 1) Use the 02BA class, not the generic MS5837:
    sensor = ms5837.MS5837_02BA()
    if not sensor.init():
        raise RuntimeError("Could not initialize MS5837_02BA")

    # 2) (Optional) If you’re in saltwater, override the default density:
    # sensor.setFluidDensity(1029.0)

    # 3) Calibrate zero at the surface:
    time.sleep(1)              # let sensor stabilize
    if not sensor.read():
        raise RuntimeError("Failed to read for zero-offset")
    surface_pressure = sensor.pressure()

    print(f"Zero-surface pressure = {surface_pressure:.1f} mbar")

    # 4) Now read depth num_read times:
    i = 0
    while i < num_read:
        if sensor.read():
            # Option A: let sensor.depth() subtract its own zero internally 
            # (it will re‐compute its own offset on each power cycle).
            depth_m = sensor.depth()
            pres = sensor.pressure()

            # OR Option B: use your own surface_pressure to adjust:
            # adj_pressure = sensor.pressure() - surface_pressure
            # depth_m = sensor.depth(adj_pressure)

            print(f"Depth: {depth_m:.3f} m   Pressure: {pres:.1f} mbar")
        else:
            print("I²C read failure")
        i += 1
        time.sleep(0.5)
