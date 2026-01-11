from gpiozero import LED


class DC:

    def __init__(self, direction_pin_1, direction_pin_2):
        self.direction_1 = LED(direction_pin_1)
        self.direction_2 = LED(direction_pin_2)
        self.pwm = LED(13)

        self.pwm.on()
        self.write_direction("off","1")
        self.write_direction("off","2")

    def write_direction(self, direction, state):
        if state == "on" and direction == "1":
            self.direction_1.on()
            print("1 on")
        elif state == "on" and direction == "2":
            self.direction_2.on()
            print("2 on")
        elif state == "off" and direction == "1":
            self.direction_1.off()
            print("1 off")
        elif state == "off" and direction == "2":
            self.direction_2.off()
            print("2 off")


