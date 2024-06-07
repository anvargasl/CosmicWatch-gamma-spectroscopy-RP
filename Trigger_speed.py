#Trigger_speed

import machine
import utime


TriggerPin = machine.Pin(16, machine.Pin.IN)

start_t = utime.ticks_us()

count = 100000
for i in range(count):
    TriggerPin.__call__()
    
dt = utime.ticks_diff(utime.ticks_us(), start_t)
print(dt/count)