#adc_test_continuous.py

import utime
import _thread
import uos, usys
import gc  #garbage collector
import machine

usys.path.insert(1, r"/drivers/")
import sdcard

#modules
import RingbufQueue

#ADC pins
sgn2 = machine.ADC(27)

b_LED = machine.Pin(14, machine.Pin.OUT)

#buffer to save data
buffer_size = 2000
event_type = [int] #saving adc reading
buffer = RingbufQueue.RingbufQueue(buffer_size, event_type)
tot_events = 2000

finished0 = False
finished1 = False

def core0_thread():
    global finished0, finished1
    global buffer
    
    dead_t = 0
    e_count = 0
    reading = None
    
    print("measuring")
    
    start_t = utime.ticks_ms()
    while e_count < tot_events:
        
        #if (e_count%1000) == 0:
        #    b_LED.on()
        #    print("0", e_count)
        #    utime.sleep_ms(5)
        #    b_LED.off()
        
        #utime.sleep_ms(5)
        #dead_t = 10
        
        reading = sgn2.read_u16()
        e_count += 1
        
        #deat_t = buffer.put([e_count,reading,dead_t])
        dead_t = buffer.put([reading])
    
    print(utime.ticks_diff(utime.ticks_ms(), start_t))
    
    finished0 = True #let core 1 know we are done measuring
    buffer._complete = True #let the buffer now it is complete
    print("0 finished", e_count)
    return

def core1_thread():
    global finished0, finished1
    global buffer
    
    e_count = 0
    events = None
    
    with open("/sd/adc_test.txt", "w") as file:
        #file.write("event,ADC_value[0-65535],dead-time\n")
        file.write("ADC_value[0-65535]\n")
    
        while e_count < tot_events:
        
            events = buffer.get() #retrieve events
            
            if not events[0][0]: break
            for event in events:
                #data = b"{}\t{}\t{}\n".format(*event)
                data = b"{}\n".format(*event)
                file.write(data)
            
            file.flush()
                
            e_count = len(events)
    
    #let core0 know we are done saving
    finished1 = True
    print("1 finished")
    return

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(5)#GPIO pinout
# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  #GPIO pinout
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))
# Initialize SD card
sd = sdcard.SDCard(spi, cs)
# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

core1 = _thread.start_new_thread(core1_thread, [])#Core 1: timmer, buffer reader

utime.sleep_ms(1000)

core0_thread()#Core 0: data collection
b_LED.on()

#Wait for core1 to be done before erasing buffer and printing to screen
f0_end_t = utime.ticks_ms()
while not finished1:
    utime.sleep_ms(10)
print("waited for reader thread",utime.ticks_diff(utime.ticks_ms(), f0_end_t), "ms")
#erase buffer
buffer = None

utime.sleep_ms(1000)
b_LED.off()

gc.collect()

print("done")