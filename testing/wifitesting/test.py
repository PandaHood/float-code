from gpiozero import LED
from time import *

red = LED(4)
start = time()
while True:

    red.on()
    sleep(1)
    red.off()
    sleep(1)
    if time() - start >= 120:
        break
