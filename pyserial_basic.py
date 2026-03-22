import serial
import time

# initializes serial connection and sends a quarter rotation positive every 2 seconds.

if __name__ == '__main__':
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	ser.reset_input_buffer()
	step_num = 200; # should be a full rotation

	while True:
		print("Sending step amount: " + str(step_num) + " to Arduino on /dev/ttyACM0")
		ser.write(str(step_num).encode('utf-8'))

		#try:
		#	while True:
		#		if ser.in_waiting > 0:
		#			line = ser.readline().decode('utf-8').rstrip()
		#			print(line)
		#except KeyboardInterrupt:
		#	print("Closing connection.")
		time.sleep(5)
