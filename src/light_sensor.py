import smbus2
import time

BH1750_ADDR = 0x23
POWER_ON = 0x01
CONT_HIGH_RES_MODE = 0x10

def init(bus=1):
    sensor = smbus2.SMBus(bus)
    sensor.write_byte(BH1750_ADDR, POWER_ON)
    sensor.write_byte(BH1750_ADDR, CONT_HIGH_RES_MODE)
    time.sleep(0.2)

    lux = read_light(sensor)
    if lux is None:
        raise RuntimeError("Could not initialize BH1750 light sensor")
    print(f"Light sensor ready: {lux:.1f} lx")

    return sensor

def read_light(sensor):
    try:
        data = sensor.read_i2c_block_data(BH1750_ADDR, CONT_HIGH_RES_MODE, 2)
    except OSError:
        return None
    return ((data[0] << 8) | data[1]) / 1.2

if __name__ == "__main__":
    sensor = init()
    print("Light sensor working - Ctrl+C to stop")
    try:
        while True:
            lux = read_light(sensor)
            if lux is None:
                print("Read failed - check wiring")
            else:
                print(f"{lux:.1f} lx")
            time.sleep(0.5)
    except KeyboardInterrupt:
        sensor.close()
