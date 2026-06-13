import serial
import time
import sys
import RPi.GPIO as GPIO

SWITCH_1_PIN = 20  # Physical Pin 38
SWITCH_2_PIN = 19  # Physical Pin 35

GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PORT      = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD_RATE = 9600

def stop_motor(ser):
    print("\nLimit switch triggered — stopping motor...")
    ser.write(("S\n").encode("utf-8"))
    time.sleep(0.5)
    print("Motor stopped.")

def main():
    print(f"Connecting to Arduino on {PORT} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
    except serial.SerialException as e:
        print(f"ERROR: Could not open port — {e}")
        sys.exit(1)

    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected!")
    print("Press Ctrl+C to stop\n")

    # Send enable command to start rotating
    ser.write(("E\n").encode("utf-8"))
    time.sleep(0.1)
    response = ser.readline().decode("utf-8").strip()
    print(f"Arduino: {response}")

    try:
        while True:
            # Check limit switches
            switch1_state = "CLOSED" if GPIO.input(SWITCH_1_PIN) == GPIO.LOW else "OPEN"
            switch2_state = "CLOSED" if GPIO.input(SWITCH_2_PIN) == GPIO.LOW else "OPEN"

            if switch1_state == "CLOSED":
                print("Switch 1 triggered!")
                stop_motor(ser)
                break

            if switch2_state == "CLOSED":
                print("Switch 2 triggered!")
                stop_motor(ser)
                break

            # Read and print any messages from Arduino
            if ser.in_waiting:
                message = ser.readline().decode("utf-8").strip()
                if message:
                    print(f"Arduino: {message}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nManually stopped.")
        stop_motor(ser)

    finally:
        ser.close()
        GPIO.cleanup()
        print("Cleanup done.")

if __name__ == "__main__":
    main()
