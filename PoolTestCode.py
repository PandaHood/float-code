#!/usr/bin/env python3
import serial
import time

def run_test_sequence(ser):
    print("\n--- Automated Test Sequence ---")
    sequence = [
        ('E',    'Enable motor'),
        ('X60',  'Set speed 60 RPM'),
        ('F200', 'Forward 200 steps'),
        ('F400', 'Forward 400 steps'),
        ('B200', 'Backward 200 steps'),
        ('R',    'Full rotation'),
        ('X30',  'Set speed 30 RPM'),
        ('F200', 'Forward 200 steps slow'),
        ('S',    'Disable motor'),
    ]
    for cmd, desc in sequence:
        print(f"\n[{cmd}] {desc}")
        ser.write(cmd + '\n')
        line = ser.readline().rstrip()
        print(f"  Arduino: {line}")
        time.sleep(1.5)
    print("\n--- Test complete ---\n")

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    time.sleep(2)  # wait for Arduino to boot

    print("Stepper Motor Test — A4988 via Arduino")
    print("Commands: F<steps>, B<steps>, X<rpm>, E, S, R, T (auto-test), Q (quit)")

    while True:
        cmd = raw_input("\nCommand > ").strip().upper()
        if not cmd:
            continue
        if cmd == 'Q':
            print("Bye.")
            break
        if cmd == 'T':
            run_test_sequence(ser)
            continue

        ser.write(cmd + '\n')
        line = ser.readline().rstrip()
        print("  Arduino: " + line)
