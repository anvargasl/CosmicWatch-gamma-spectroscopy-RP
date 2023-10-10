from machine import Pin
from utime import sleep

led = Pin(25, Pin.OUT)

while True:
    sleep(2)
    led.toggle()