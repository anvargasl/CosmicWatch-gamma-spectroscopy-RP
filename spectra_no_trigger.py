#spectra_no_trigger

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

b_LED = machine.Pin(14, machine.Pin.OUT)

#buffer to save data
buffer_size = 200
buffer = RingbufQueue.RingbufQueue(buffer_size)
tot_events = 1000
t1_e_count = 0
rate = 0

isotope = "bkgd"

finished0 = False
finished1 = False

def core1_thread():
    global finished0, finished1
    global tot_events
    global buffer
    
    prev_t = 0
    new_t = 0
    
    e_count = 0
    events = None
    
    #with open("/sd/"+isotope+"-"+str(tot_events)+".txt", "w") as file:
    with open("/sd/test.txt", "w") as file:
        file.write("ADC_value[0-65535]\n")
    
        while e_count < tot_events:
            events = buffer.get()
            e_count += len(events)
                    
            for event in events:
                data = b"{}\t{}\t{}\n".format(*event)
                file.write(data)
            
            if e_count % 1000 == 0:
                print(e_count)
                file.flush()
    
    #let core0 know we are done saving
    finished1 = True
    print("1 finished")

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

#global finished0
#global tot_events
#global buffer

utime.sleep_ms(2000)
#start_t = utime.ticks_ms()

e_count = 0
dead_t = 0
print("measuring")
readings = [0]
while e_count < tot_events:     
    #e_count, dead_t = write_bf(start_t, e_count, dead_t)
    
    while not TriggerPin.value():
        continue
        
    readings[0] = sgn2.read_u16() #this seems slightly better than saving the global function
    #readings[1] = sgn2.read_u16()
    #readings[2] = sgn2.read_u16()
    #readings[3] = sgn2.read_u16()
    #readings[4] = sgn2.read_u16()
    
    TriggerResetPin.on()
    TriggerResetPin.off()
    
    b_LED.on()

    e_count += 1
    
    deat_t = buffer.put([e_count]+readings+[dead_t])

    b_LED.off()

finished0 = True
print("0 finished", e_count)

#Wait for core1 to be done before erasing buffer and printing to screen
#lock.acquire()
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
