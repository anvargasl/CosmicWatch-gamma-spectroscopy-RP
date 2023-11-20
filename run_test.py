import utime
import _thread
import sys
from machine import Pin

#drivers
sys.path.insert(1, r"/drivers/")
from bmp280 import *
#modules
import OLED

new_thread = _thread.start_new_thread(OLED.display_task, (0, "timer"))
utime.sleep_ms(1000)

def run_multi_thread():
    led = Pin(15, Pin.OUT)
    
    i2c_dev, ident = OLED.init_i2c(0, scl_pin=13, sda_pin=12)
    #Temperature sensor
    bmp = BMP280(i2c_dev)
    bmp.use_case(BMP280_CASE_INDOOR)
    
    sgn2 = machine.ADC(26)
    ident = str(_thread.get_ident())

    pressure=bmp.pressure
    p_bar=pressure/100000
    p_mmHg=pressure/133.3224
    temp=bmp.temperature
    print("Temperature: {} C".format(temp))
    print("Pressure: {} Pa, {} bar, {} mmHg".format(pressure,p_bar,p_mmHg))
    utime.sleep_ms(100)

    atm_p = 101325
    
    counter = 0
    start_time = utime.ticks_us()
    while counter<100:
        reading = sgn2.read_u16()
        ds = (utime.ticks_diff(utime.ticks_us(), start_time) // 1000)
        
        if reading > 1000:
            counter += 1
            temp = bmp.temperature
            print("ADC: ", ident, counter, ds, temp, (pressure-atm_p)/atm_p, reading)
            led.on()
            utime.sleep_ms(100)
            led.off()
            utime.sleep_ms(100)
    
    #Start_SD_card()
    
if __name__ == '__main__':
    run_multi_thread()
