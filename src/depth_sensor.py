import ms5837
import time 

def init():
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

    return sensor
# Print readings
def read_depth(sensor):
    # Trigger a new I2C read; returns True on success
    if not sensor.read():
        return None, None
    # You can either use sensor.depth() (which applies default density)
    # or compute depth from an adjusted pressure:
    return sensor.depth(), sensor.pressure()