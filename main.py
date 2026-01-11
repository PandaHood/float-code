import time
import datetime
import ms5837

import src.util as util 
import src.depth_sensor as depth_sensor
import src.dc_motor as motor

## Main loop
def main():
   
    sensor = depth_sensor.init()
    dcmotor = motor.DC(22,23)


    start = time.time()
    end = time.time()
    fail = 0
    for _ in range(100):
        try:
            print("Before")
            dcmotor.write_direction("1", "on")
            time.sleep(0.2)
            dcmotor.write_direction("1", "off")
            time.sleep(0.2)
            dcmotor.write_direction("2", "on")
            time.sleep(0.2)
            dcmotor.write_direction("2", "off")
            time.sleep(0.2)

            print(depth_sensor.read_depth(sensor))


            end = time.time()
            time.sleep(1)
        except:
            fail+=1
    print(fail)




if __name__ == "__main__":
    main()