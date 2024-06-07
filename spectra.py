#spectra

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
sgn2 = machine.ADC(26)
TriggerPin = machine.Pin(16, machine.Pin.IN)
TriggerResetPin = machine.Pin(21, machine.Pin.OUT)

interrupt_flag = 1

b_LED = machine.Pin(14, machine.Pin.OUT)

#buffer to save data
buffer_size = 200
event_type = [int,int,int] #saving e_count, adc reading, dead time
buffer = RingbufQueue.RingbufQueue(buffer_size, event_type)
tot_events = 100000

start_t = utime.ticks_ms()
mins_elapsed = divmod((utime.ticks_diff(utime.ticks_ms(), start_t) // 1000), 60)[0]
measure_t = 60 #mins
print(mins_elapsed)

finished0 = False
finished1 = False

def core0_thread():
    global finished0, finished1
    global mins_elapsed
    global interrupt_flag
    global buffer
    
    e_count = 0
    dead_t = 0
    
    print("measuring")
    interrupt_flag = 0
    
    #while e_count < tot_events:
    while mins_elapsed < measure_t:
        #e_count, dead_t = write_bf(start_t, e_count, dead_t)
        
        #print("measuring1")
        if interrupt_flag:
            
            e_count += 1
            
            deat_t = buffer.put([e_count]+readings+[dead_t])

            b_LED.off()
            
            #if e_count < tot_events:
            interrupt_flag = 0
                
        mins_elapsed = divmod((utime.ticks_diff(utime.ticks_ms(), start_t) // 1000), 60)[0]
    
    finished0 = True #let core 1 know we are done measuring
    buffer._complete = True #let the buffer now it is complete
    print("0 finished", e_count)
    return

def core1_thread():
    global finished0, finished1
    global buffer
    global mins_elapsed
    
    prev_t = 0
    new_t = 0
    
    events = None
    
    prev_min = mins_elapsed
    with open("/sd/main.txt", "w") as file:
        file.write("event,ADC_value[0-65535],dead-time\n")
    
        #while e_count < tot_events:
        while not finished0: #check if we are still measuring
        
            events = buffer.get() #retrieve events
            
            if events[0][0]: #write only if there are unread events
            #if not buffer._complete or not buffer.empty():
                for event in events:
                    data = b"{}\t{}\t{}\n".format(*event)
                    file.write(data)
            
            if mins_elapsed > prev_min:
                file.flush()
                print(mins_elapsed)
                prev_min = mins_elapsed
    
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

#Core 1: timmer, buffer reader
core1 = _thread.start_new_thread(core1_thread, [])
#Core 0: data collection
#core0_thread()

readings = [0]
@micropython.native
def read_ADC(TriggerPin): #interrupt routine
    reading = sgn2.read_u16()
    TriggerResetPin.on()
    TriggerResetPin.off()
    global interrupt_flag
    global readings
    
    if interrupt_flag == 0:
        
        readings[0] = reading #this seems slightly better than saving the global function
        
        b_LED.on()
        
        interrupt_flag = 1
    
TriggerPin.irq(trigger=machine.Pin.IRQ_RISING, handler=read_ADC)

utime.sleep_ms(1000)

core0_thread()
b_LED.off()

#Wait for core1 to be done before erasing buffer and printing to screen
f0_end_t = utime.ticks_ms()
while not finished1:
    utime.sleep_ms(10)
print("waited for reader thread",utime.ticks_diff(utime.ticks_ms(), f0_end_t), "ms")
#erase buffer
buffer = None
gc.collect()

print("done")
#with open("/sd/test01.txt", "r") as file:
#    print(file.read())