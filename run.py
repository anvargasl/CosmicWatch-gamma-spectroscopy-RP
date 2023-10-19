import utime
import OLED
import _thread
        
def run_multi_thread():
    
    #Id = 0 :CosmicWatch  OLED configuration
    new_thread = _thread.start_new_thread(OLED.display_task, (0, "timer"))
    
    sgn2 = machine.ADC(26)
    ident = str(_thread.get_ident())
 
    counter = 0
    start_time = utime.ticks_us()
    while True:
        reading = sgn2.read_u16()
        ds = (utime.ticks_diff(utime.ticks_us(), start_time) // 1000)
        
        if reading > 1:
            counter += 1
            print("ADC: ", ident, counter, ds, reading)
    
if __name__ == '__main__':
    run_multi_thread()
