import serial
import time
import sys
import RPi.GPIO as GPIO

SWITCH_1_PIN = 20  # Physical Pin 38
SWITCH_2_PIN = 19  # Physical Pin 35

GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PORT      = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyS0"
BAUD_RATE = 9600

def send_command(ser, cmd):
    ser.write((cmd + "\n").encode("utf-8"))
    time.sleep(0.1)

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

    # Start moving forward
    direction = "F"  # F = forward, B = backward
    send_command(ser, "E")
    send_command(ser, direction)
    print("Motor started moving forward")

    try:
        while True:
            switch1_state = "CLOSED" if GPIO.input(SWITCH_1_PIN) == GPIO.LOW else "OPEN"
            switch2_state = "CLOSED" if GPIO.input(SWITCH_2_PIN) == GPIO.LOW else "OPEN"

            if switch1_state == "CLOSED" and direction == "F":
                print("Switch 1 triggered — reversing to backward!")
                direction = "B"
                send_command(ser, "S")   # stop first
                time.sleep(0.3)
                send_command(ser, "B")   # go backward
                time.sleep(0.5)          # debounce delay

            if switch2_state == "CLOSED" and direction == "B":
                print("Switch 2 triggered — reversing to forward!")
                direction = "F"
                send_command(ser, "S")   # stop first
                time.sleep(0.3)
                send_command(ser, "F")   # go forward
                time.sleep(0.5)          # debounce delay

            # Read and print any messages from Arduino
            if ser.in_waiting:
                message = ser.readline().decode("utf-8").strip()
                if message:
                    print(f"Arduino: {message}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nManually stopped.")
        send_command(ser, "S")

    finally:
        ser.close()
        GPIO.cleanup()
        print("Cleanup done.")

if __name__ == "__main__":
    main()
