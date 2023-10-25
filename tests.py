from machine import Pin
import utime, machine, usys, gc, micropython 
#machine.freq(125000000*2)

LED = Pin("LED", Pin.OUT)
LED.on(); utime.sleep_ms(1000); LED.off() # no resets detected

print(1009//1000)

data = b'x'*10000+b'\n'
while True:
    for a in range(1000):
        try:
            usys.stdout.buffer.write(data)  
        except:
            LED.on(); utime.sleep_ms(200); LED.off() # no errors detected
    utime.sleep_us(1) # try allowing USB stack to flush (no effect on later speed)