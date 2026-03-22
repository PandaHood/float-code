import RPi.GPIO as GPIO
import time

DIRECTION_PIN = 31

# Use board pin-numbering scheme
GPIO.setmode(GPIO.BOARD) 

# Set the pin as an output
GPIO.setup(DIRECTION_PIN, GPIO.OUT) 

try:
    # direction pin set to high
    GPIO.output(DIRECTION_PIN, GPIO.HIGH) 
    print("direction pin high")
    time.sleep(1) # Wait for 1 second

    # direction pin set to low
    GPIO.output(DIRECTION_PIN, GPIO.LOW) 
    print("direction pin low")

except KeyboardInterrupt:
    # Clean up GPIO settings on Ctrl+C
    pass

finally:
    # Good practice to clean up at the end of the program
    GPIO.cleanup()
