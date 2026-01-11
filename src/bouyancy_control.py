# Imports
from datetime import datetime, timezone
import RPi.GPIO as GPIO     
import time

# Our modules
from ms5837 import MS5837
from stepper import TicI2C


class FloatController:
    def __init__(self):
        # Class imports
        self.depth_sensor = MS5837(model='MS5837_02BA')
        self.stepper = TicI2C()

        # Initial Variable Assignments
        self.extend_limit_pin = 2 # Input pin for hitting the max extension (positively bouyant)
        self.retract_limit_pin = 3 # Input pin for hitting the max retraction (negatively bouyant)
        self.explorer_team = "EX06"
        self.filename = "profile.txt"
        self.start_time = time.time()
        self.times_logged = 0
        self.times_logged_at_depth = 0
        self.total_steps = 0 # Assign to an expected value at some point
        self.current_position = 0 # Current position of the motor. 0 is fully extended, total_steps is retracted
        self.waiting_for_input = False

        # Tunable Parameters
        self.time_per_step_size = 0.5 # the maximum time it takes to go a certain step size (TO BE TESTED)
        self.step_size = 100 # number of steps taken when maxing bouyancy
        self.log_frequency = 5 # the number of seconds 
        self.bang_bang_radius = 0.1 # meters of buffer where we let our bouyancy be
        self.target_radius = 0.5 # meters of allowed buffer around our targer
        self.target_depth = 2.5 # targer depth in meters
        self.depth_hold_time = 45
        self.midpoint_ratio = 0.5 # midpoint of the bouyancy engine
        self.max_depth_hold_time = 240 # maximum number of seconds to attempt to depth hold before ascending
        self.ascension_break_depth = 0.5 # the depth to break the ascension loop
        
        # GPIO setup
        GPIO.setmode(GPIO.BCM)  # Set's GPIO pins to BCM GPIO numbering
        GPIO.add_event_detect(self.extend_limit_pin, GPIO.FALLING, callback=self.extend_limit, bouncetime=200)
        GPIO.add_event_detect(self.retract_limit_pin, GPIO.FALLING, callback=self.retract_limit, bouncetime=200)
        GPIO.add_event_detect(self.extend_limit_pin, GPIO.RISING, callback=self.extend_unlimit, bouncetime=200)
        GPIO.add_event_detect(self.retract_limit_pin, GPIO.RISING, callback=self.retract_unlimit, bouncetime=200)
        GPIO.setup(self.extend_limit_pin, GPIO.IN)  # Set our input pin to be an input
        GPIO.setup(self.retract_limit_pin, GPIO.IN)  # Set our input pin to be an input

        # Initialize values and prepare to start
        self.at_extension_limit = GPIO.input(self.extend_limit_pin)
        self.at_retraction_limit = GPIO.input(self.retract_limit_pin)
        self.stepper.exit_safe_start()


    def run_mission(self):
        # start by going to maximum positive bouyancy
        self.max_positive_bouyancy()

        # ensure logging is working
        while self.times_logged < 5:
            self.add_log_entry()

        # go to max negative bouyancy and count how many steps that takes
        self.max_negative_bouyancy(update_count=True)
        self.descend_to_depth()

        # we should be at 2 meters deep. Try to decelerate and hold at 2.5m
        self.hold_depth()
        self.ascend_to_surface()
        self.wait_for_transfer()

        # Do it again
        self.descend_to_depth()
        self.hold_depth()
        self.ascend_to_surface()
        self.wait_for_transfer()

    def run_trash_mission(self):
        # start by going to maximum positive bouyancy
        self.max_positive_bouyancy()

        # ensure logging is working
        while self.times_logged < 5:
            self.add_log_entry()

        # go to max negative bouyancy and count how many steps that takes
        self.max_negative_bouyancy(update_count=True)
        while self.times_logged < 15:
            self.add_log_entry()

        self.max_positive_bouyancy(update_count=True)


    # Mission Methods
    def max_positive_bouyancy(self):
        prev_time = time.time()
        while not self.extend_limit:
            if time.time() - prev_time > self.time_per_step_size:
                self.stepper.set_target_position(self.step_size)
                prev_time = time.time()
            self.add_log_entry()
        

    def max_negative_bouyancy(self, update_count=False):
        prev_time = time.time()
        # reset the total steps if we are updating the count
        if update_count:
            self.total_steps = 0 
        while not self.retract_limit:
            if time.time() - prev_time > self.time_per_step_size:
                self.stepper.set_target_position(-self.step_size)
                # update the total steps if we are updating the count
                if update_count:
                    self.total_steps += self.step_size
                prev_time = time.time()
            self.add_log_entry()
        

    def descend_to_depth(self):
        self.waiting_for_input = False
        # TOASK: should we get closer in before we start slowing down?
        while self.depth_sensor.depth() > self.target_depth - self.target_radius:
            self.add_log_entry()
            if not self.retract_limit:
                self.max_negative_bouyancy()

    def hold_depth(self):
        depth_hold_start_time = time.time()
        self.times_logged_at_depth = 0

        # We make sure we have logged 1 more time that the needed number in the zone
        while (self.times_logged_at_depth * self.log_frequency + 1 <= self.depth_hold_time or 
               time.time() - depth_hold_start_time > self.max_depth_hold_time):
            self.add_log_entry()
            self.step_to_position()
            

    def ascend_to_surface(self):
        while self.depth_sensor.depth() < self.ascension_break_depth:
            self.add_log_entry()
            if not self.extend_limit:
                self.max_positive_bouyancy()
    
    def wait_for_transfer(self):
        # this method might hold on input and create a logging buildup
        self.waiting_for_input = True
        user_input = input("Please input command to continue: ")
        while user_input != "continue" or user_input != "c":
            self.add_log_entry()
            if user_input == "transfer" or user_input == "t":
                self.transfer_file()
            user_input = input("Please input command to continue:")
            
    # General Methods
    def extend_limit(self):
        self.at_extension_limit = True
        self.current_position = 0

    def retract_limit(self):
        self.at_retraction_limit = True
        self.current_position = self.total_steps

    def extend_unlimit(self):
        self.at_extension_limit = False

    def retract_unlimit(self):
        self.at_retraction_limit = False

    # need a better method name
    def step_to_position(self):
        current_depth = self.depth_sensor.depth()
        ratio = (self.target_depth - current_depth) / self.target_radius
        midpoint = self.total_steps * self.midpoint_ratio
        if ratio > 1:
            self.max_negative_bouyancy()
        elif ratio < -1:
            self.max_positive_bouyancy()
        elif ratio > self.bang_bang_radius:
            target_pos = (self.total_steps - midpoint) * ratio + midpoint
            self.step_to_target_pos_with_wait(target_pos)
        elif ratio < -self.bang_bang_radius:
            target_pos = (self.total_steps - midpoint) * ratio + midpoint
            self.step_to_target_pos_with_wait(target_pos)
        else: # we are in the bang bang region
            self.step_to_target_pos_with_wait(midpoint)

    def step_to_target_pos_with_wait(self, target_pos):
        steps_to_take = target_pos - self.current_position
        while (abs(steps_to_take) > self.step_size and
               not self.retract_limit and not self.extend_limit):
            self.add_log_entry()
            if steps_to_take > 0:
                self.safe_step(self.step_size, self.time_per_step_size)
                steps_to_take -= self.step_size
            if steps_to_take < 0:
                self.safe_step(-self.step_size, self.time_per_step_size)
                steps_to_take += self.step_size

    def safe_step(self, step_size, wait_time):
        start_time = time.time()
        self.stepper.set_target_position(step_size)
        # This method of waiting is highly questionable, but I don't want to sleep for logging
        while time.time() - start_time > wait_time:
            self.add_log_entry()
        self.current_position += step_size
        return "success"
    
    def transfer_file(self):
        f = open(self.filename)
        lines = f.readlines()
        for line in lines:
            print(line)

    def add_log_entry(self):
        # This need to be put into all hot loops
        utc_time = datetime.now(timezone.utc)
        pressure = self.depth_sensor.pressure()
        depth = self.depth_sensor.depth()
        if time.time() - self.start_time > self.log_frequency * self.times_logged:
           
            self.times_logged += 1
            if self.target_depth - self.target_radius < depth < self.target_depth + self.target_radius:
                self.times_logged_at_depth +=1
            print(f"Data Point {self.times_logged}: {self.explorer_team}, {utc_time}, {depth}, {pressure}")
            if self.waiting_for_input:
                print("Please input command to continue")


