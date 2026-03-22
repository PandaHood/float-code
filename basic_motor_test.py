import RPi.GPIO as GPIO
from time import sleep

DIRECTION_PIN = 31			  # GPIO pin connected to A4988 DIR pin
STEP_PIN = 32                             # PWM pin connected to A4988 STEP pin

GPIO.setmode(GPIO.BOARD)                #set pin numbering system
GPIO.setup(DIRECTION_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN,GPIO.OUT)
pi_pwm = GPIO.PWM(STEP_PIN,1000000)          #create PWM instance with frequency
pi_pwm.start(0)                         #start PWM of required Duty Cycle
while True:
    GPIO.output(DIRECTION_PIN, GPIO.HIGH)
    print("direction pin high")
    sleep(0.5) # Wait for half a second
    pi_pwm.ChangeDutyCycle(0.5) #provide duty cycle in the range 0-100
    sleep(0.5)

    GPIO.output(DIRECTION_PIN, GPIO.LOW)
    print("direction pin low")
    sleep(0.5) # Wait for half a second
    pi_pwm.ChangeDutyCycle(0.5)
    sleep(0.5)
