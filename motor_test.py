from src.stepper import *

if __name__ == "__main__":
     
    # Open a handle to "/dev/i2c-3", representing the I2C bus.
    bus = SMBus(1)
    
    # Select the I2C address of the Tic (the device number).
    address = 14
    
    tic = TicI2C(bus, address)

    position = tic.get_current_position()
    print("Current position is {}.".format(position))
    
    new_target = -200 if position > 0 else 200
    new_target = int(input("Position: "))
    print("Setting target position to {}.".format(new_target))
    tic.exit_safe_start()
    tic.set_target_position(new_target)