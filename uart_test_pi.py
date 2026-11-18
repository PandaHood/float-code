#!/usr/bin/env python3
import serial
import time

PORT      = "/dev/ttyS0"
BAUD_RATE = 9600

if __name__ == '__main__':
    print(f"Opening {PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()
    print("Connected! Sending test messages...\n")

    count = 1
    while True:
        message = f"Hello from Pi #{count}\n"
        ser.write(message.encode('utf-8'))
        print(f"Pi sent:     {message.strip()}")

        line = ser.readline().decode('utf-8').rstrip()
        if line:
            print(f"Arduino got: {line}")
        else:
            print("Arduino got: (no response — check wiring/baud)")

        count += 1
        time.sleep(1)
