import sys
import time
import csv
import serial
import RPi.GPIO as GPIO
import ms5837
from datetime import datetime, timezone

POSITIVE_LIMIT_PIN  = 20
NEGATIVE_LIMIT_PIN = 19

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD_RATE = 9600
LOG_FILE_PATH = "depth_log.csv"
COMPANY_ID = "EX11"

FLUID_DENSITY_SALTWATER = 1029.0
IS_SALTWATER = False

FLOAT_HEIGHT_M = 0.4699
SENSOR_FROM_BOTTOM_M = 0.0889
SENSOR_FROM_TOP_M = FLOAT_HEIGHT_M - SENSOR_FROM_BOTTOM_M

PUMP_POSITIVE_COMMAND = "B"
PUMP_NEGATIVE_COMMAND = "F"

BANG_BANG_RANGE_M = 0.50
SUBMERGE_STEP_S = 0.1
SUBMERGE_CORRECTION_S = 0.4
CONTROL_STEP_S = 0.1
LOG_INTERVAL_S = 5.0
HOLD_DURATION_S = 30.0
VELOCITY_DEADBAND = 0.005
BANG_BANG_ALPHA = 0.7
MAX_VELOCITY = 0.03

DEEP_TARGET_M = 2.50
SHALLOW_TARGET_M = 0.40
ACCEPTABLE_TARGET_ERROR_M = 0.33

DEEP_SENSOR_TARGET_M = DEEP_TARGET_M - SENSOR_FROM_BOTTOM_M
SHALLOW_SENSOR_TARGET_M = SHALLOW_TARGET_M + SENSOR_FROM_TOP_M

class FloatController():

    def __init__(self):
        self.ser = None
        self.sensor = None
        self.surface_p = None
        self.log_writer = None
        self.log_buffer = []
        self.last_log_time = 0.0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(POSITIVE_LIMIT_PIN,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(NEGATIVE_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def utc_datetime_formatted(self):
        return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


    def send_cmd(self, cmd):
        self.ser.write((cmd + "\n").encode("utf-8"))
        time.sleep(0.05)


    def is_fully_positive(self):
        return GPIO.input(POSITIVE_LIMIT_PIN) == GPIO.LOW


    def is_fully_negative(self):
        return GPIO.input(NEGATIVE_LIMIT_PIN) == GPIO.LOW


    def read_depth(self):
        if not self.sensor.read():
            print("Warning: Could not read depth.")
            return None
        return self.sensor.depth()


    def pressure_pa(self):
        return self.sensor.pressure() * 100.0


    def log_packet(self, depth_m):
        t = time.monotonic()
        if t - self.last_log_time >= LOG_INTERVAL_S:
            pkt = f"{COMPANY_ID} {self.utc_datetime_formatted()} {self.pressure_pa()/1000:.2f} kPa {depth_m:.3f} m"
            self.log_buffer.append(pkt)
            self.log_writer.writerow([self.utc_datetime_formatted(), round(depth_m, 3), round(self.pressure_pa(), 2)])
            print(pkt)
            self.last_log_time = t


    def make_negative(self, duration):
        if not self.is_fully_negative():
            self.send_cmd(PUMP_NEGATIVE_COMMAND)
            time.sleep(duration)
            # self.send_cmd("S")


    def make_positive(self, duration):
        if not self.is_fully_positive():
            self.send_cmd(PUMP_POSITIVE_COMMAND)
            time.sleep(duration)
            # self.send_cmd("S")


    def submerge(self):
        print("ENTERING STATE: submerge")
        self.make_negative(7.0)
        self.send_cmd("S")
        while True:
            depth = self.read_depth()
            if depth is None:
                continue
            self.log_packet(depth)
            if depth > 0.8:
            #    self.make_positive(SUBMERGE_CORRECTION_S)
                self.send_cmd("S")
                return
            self.make_negative(SUBMERGE_STEP_S)
            self.send_cmd("S")
            time.sleep(5.0)


    def sink(self, target_sensor_depth):
        print(f"ENTERING STATE: sink -> {target_sensor_depth:.3f} m")
        prev_depth = self.read_depth()
        prev_time = time.monotonic()
        vel_error_count = 0
        while True:
            time.sleep(CONTROL_STEP_S)
            depth = self.read_depth()
            if depth is None:
                continue
            self.log_packet(depth)
            dt = time.monotonic() - prev_time
            # if dt > 0 and prev_depth is not None:
            #    velocity = (depth - prev_depth) / dt
            #    if velocity < 0:
            #        vel_error_count += 1
            #        if vel_error_count >=2:
            #            self.make_negative(CONTROL_STEP_S)
            #            self.send_cmd("S")
            #            vel_error_count = 0
            prev_depth = depth
            prev_time  = time.monotonic()
            if depth >= target_sensor_depth - BANG_BANG_RANGE_M:
                return


    def bang_bang(self, target_sensor_depth, step_duration):
        print(f"ENTERING STATE: bang-bang @ {target_sensor_depth:.3f} m sensor depth")
        # upper_bound = target_sensor_depth - 1.0
        # lower_bound = target_sensor_depth + 1.0
        in_range_since = None
        direction = 1

        smoothed = self.read_depth()
        while smoothed is None:
            smoothed = self.read_depth()
        prev_smoothed = smoothed
        prev_time = time.monotonic()
        velocity = 0.0

        while True:
            raw = self.read_depth()
            if raw is None:
                continue
            self.log_packet(raw)

            smoothed = BANG_BANG_ALPHA * raw + (1 - BANG_BANG_ALPHA) * smoothed
            t = time.monotonic()
            dt = t - prev_time

            if dt > 0 and prev_smoothed is not None:
                velocity = (smoothed - prev_smoothed) / dt
                if abs(velocity) > VELOCITY_DEADBAND:
                    direction = 1 if velocity >= 0.0 else -1
                else:
                    direction = 0

            prev_smoothed = smoothed
            prev_time = t

            if smoothed < target_sensor_depth + ACCEPTABLE_TARGET_ERROR_M and smoothed > target_sensor_depth - ACCEPTABLE_TARGET_ERROR_M:
                if in_range_since is None:
                    in_range_since = time.monotonic()
                elif time.monotonic() - in_range_since >= HOLD_DURATION_S:
                    self.send_cmd("S")
                    print(f"SUCCESS: Held {HOLD_DURATION_S:.0f} s at {target_sensor_depth:.3f} m")
                    return
            else:
                in_range_since = None

            if ((smoothed < target_sensor_depth and (direction == -1 or direction == 0)) or (velocity < -1 * MAX_VELOCITY)) and not self.is_fully_negative():
                self.send_cmd(PUMP_NEGATIVE_COMMAND)
            elif ((smoothed > target_sensor_depth and (direction == 1 or direction == 0)) or (velocity > MAX_VELOCITY)) and not self.is_fully_positive():
                self.send_cmd(PUMP_POSITIVE_COMMAND)
            else:
                self.send_cmd("S")

            time.sleep(0.05)


    def ascend(self, target_sensor_depth):
        print(f"ENTERING STATE: ascend -> {target_sensor_depth:.3f} m")
        prev_depth = self.read_depth()
        prev_time  = time.monotonic()
        vel_error_count = 0
        while True:
            time.sleep(CONTROL_STEP_S)
            depth = self.read_depth()
            if depth is None:
                continue
            self.log_packet(depth)
            dt = time.monotonic() - prev_time
            # if dt > 0 and prev_depth is not None:
            #     velocity = (depth - prev_depth) / dt
            #     if velocity > 0:
            #         vel_error_count += 1
            #         if vel_error_count >= 2:
            #             self.make_positive(CONTROL_STEP_S)
            #             vel_error_count = 0
            prev_depth = depth
            prev_time  = time.monotonic()
            if depth <= target_sensor_depth + BANG_BANG_RANGE_M:
                return


    def return_to_surface(self):
        print("ENTERING STATE: return to surface")
        while not self.is_fully_positive():
             self.send_cmd(PUMP_POSITIVE_COMMAND)
             time.sleep(0.1)
        self.send_cmd("S")
        print("SUCCESS: Fully positive; float at surface.")


    def main(self):
        self.sensor = ms5837.MS5837_02BA()
        if not self.sensor.init():
            raise RuntimeError("Sensor init failed")
        if IS_SALTWATER:
            self.sensor.setFluidDensity(FLUID_DENSITY_SALTWATER)
        time.sleep(5)
        if not self.sensor.read():
            raise RuntimeError("Initial sensor read failed")
        surface_p = self.sensor.pressure()
        print(f"Surface pressure: {surface_p:.2f} mbar")

        self.ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        self.ser.reset_input_buffer()

        deep_bb_target = DEEP_SENSOR_TARGET_M
        shallow_bb_target = SHALLOW_SENSOR_TARGET_M

        self.send_cmd("E")

        with open(LOG_FILE_PATH, mode='w', newline='') as csv_file:
            self.log_writer = csv.writer(csv_file)
            self.log_writer.writerow(["Timestamp (UTC)", "Depth (m)", "Pressure (Pa)"])

            states = [
                ("return_surface", lambda: self.return_to_surface()),
                ("submerge", lambda: self.submerge()),
                # ("sink_deep", lambda: self.sink(deep_bb_target)),
                ("bang_bang_deep", lambda: self.bang_bang(deep_bb_target, CONTROL_STEP_S)),
                # ("ascend_shallow", lambda: self.ascend(shallow_bb_target)),
                ("bang_bang_shallow_1", lambda: self.bang_bang(shallow_bb_target, CONTROL_STEP_S)),
                # ("sink_deep_2", lambda: self.sink(deep_bb_target)),
                ("bang_bang_deep_2", lambda: self.bang_bang(deep_bb_target, CONTROL_STEP_S)),
                # ("ascend_shallow_2", lambda: self.ascend(shallow_bb_target)),
                ("bang_bang_shallow_2", lambda: self.bang_bang(shallow_bb_target, CONTROL_STEP_S)),
                ("return_surface", lambda: self.return_to_surface()),
            ]

            for _, fn in states:
                fn()

        print("\nAll packets:")
        for pkt in self.log_buffer:
            print(" ", pkt)
        print(f"\nLog saved to {LOG_FILE_PATH}")
        self.ser.close()
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        ctrl = FloatController()
        ctrl.main()
    except Exception as e:
        print(f"FATAL: {e}")
        GPIO.cleanup()
        sys.exit(1)
