#run.py

import utime
import _thread
import uos, usys
import gc  #garbage collector
import random as rand
import machine

usys.path.insert(1, r"/drivers/")
from ssd1306 import SSD1306_I2C
from bmp280 import *
import sdcard

#modules
import OLED
#import sd_module
import RingbufQueue

#detector name
name = "green"
role = "M"

#Coincidence pins
COINCIDENCE = None
coincident_= signal_input_pin  = None
coincident_signal_output_pin = None

#ADC pins
sgn2 = machine.ADC(26)

Temp = 0
Pres = 0

b_LED = machine.Pin(14, machine.Pin.OUT)
s_LED = machine.Pin(15, machine.Pin.OUT)

#OLED
addr_dict = {"blue": 0x3D, "green": 0x3C}
oled_id = None
pix_res_x = 128
pix_res_y = 64

#buffer to save data
buffer_size = 200
buffer = RingbufQueue.RingbufQueue(buffer_size)
tot_events = 6000
t1_e_count = 0
rate = 0

finished0 = False
finished1 = False

#global start time
start_t = 0
rtc = machine.RTC()

def CoincidentMode():
    global role
    global COINCIDENCE
    global coincident_signal_input_pin
    global coincident_signal_output_pin
    
    coincident_pin_1 = machine.Pin(19, machine.Pin.IN)
    coincident_pin_2 = None
    
    #if someone is talking to me in channel 1, then talk in chanel 2
    print(coincident_pin_1.value())
    if coincident_pin_1.value():
        coincident_pin_2 = machine.Pin(20, machine.Pin.OUT)
        coincident_pin_2.on()
        coincident_signal_input_pin  = coincident_pin_1
        coincident_signal_output_pin = coincident_pin_2
        
        b_LED.on()
        s_LED.on()
        utime.sleep_ms(1000)
        b_LED.off()
        s_LED.off()
        coincident_pin_2.off()
        
        COINCIDENCE = True #Another detector observed
        #filename[4] = ‘C’;
        print("Coincidence detector found, "+name+" is slave")
        role = "S"
        #utime.sleep_ms(2000)
        
        return

    else: #if nobody is talking to me in channel 1, then talk in channel 1
        coincident_pin_1 = machine.Pin(19, machine.Pin.OUT)
        coincident_pin_1.on()
        coincident_pin_2 = machine.Pin(20, machine.Pin.IN)
        #filename[4] = ‘M’; // Label the filename as “M”aster
        utime.sleep_ms(1000)
        for i in range(0,101):
            print(name+" waiting")
            
            if coincident_pin_2.value():
                coincident_signal_input_pin  = coincident_pin_2
                coincident_signal_output_pin = coincident_pin_1

                b_LED.on()
                s_LED.on()
                utime.sleep_ms(1000)
                b_LED.off()
                s_LED.off()
                coincident_pin_1.off()

                COINCIDENCE = True # Another detector observed
                #filename[4] = ‘C’;  // Label the filename as “C”oincidence
                print("Coincidence detector found, "+name+" is master")
                
                return
            
            utime.sleep_ms(10)
        
        coincident_pin_1.off()

#I2C port
i2c_dev, oled_id = OLED.init_i2c()

#temperature sensor
bmp = BMP280(i2c_dev)
bmp.use_case(BMP280_CASE_INDOOR)

Temp = bmp.temperature
Pres = bmp.pressure

#OLED display
oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev, addr=addr_dict[name])
oled.rotate(False)

OLED.display_logo(oled) #Login screen

#showing elapsed time
OLED.display_text(oled, line=0, text="Thread:"+str(oled_id))
#OLED.display_text(oled, line=0, start=58, text=str(oled_id))
OLED.display_text(oled, line=0, start=70, text="Role:"+role)
OLED.display_text(oled, line=1, text="Uptime:")
OLED.display_text(oled, line=2, text="Count:")
OLED.display_text(oled, line=3, text="Temp:")
OLED.display_text(oled, line=4, text="Rate:")
oled.rect(0,0,pix_res_x,pix_res_y,1)
oled.show()

#def update_OLED(oled, bmp, prev_t, new_t, e_count):
def update_OLED(prev_t, new_t, e_count):
    #global start_t
    #global oled_id
    global Temp, Pres
    global rate
    
    l_start = 58
    
    new_t = (utime.ticks_diff(utime.ticks_ms(), start_t) // 1000)# + 1
    
    if new_t > prev_t:
        mins, sec = divmod(new_t, 60)
        hour, mins = divmod(mins, 60)
        uptime = '%d:%02d:%02d' % (hour, mins, sec)
    
        #oled.fill_rect(l_start, 2+1*(8+2), width, height, 0)
        OLED.erase_line(oled, line=1, start=l_start)
        OLED.display_text(oled, line=1, start=l_start, text=uptime)
        
        prev_t = new_t
    
    if e_count > t1_e_count:
        Temp = bmp.temperature
        Pres = bmp.pressure
        if new_t > 0:
            rate = round(e_count/new_t,3)
        else:
            rate = 0
        
        OLED.erase_lines(oled, lines=[2,4], start=l_start)
    
        OLED.display_text(oled, line=2, start=l_start, text=str(e_count))
        OLED.display_text(oled, line=3, start=l_start, text=str(Temp))
        OLED.display_text(oled, line=4, start=l_start, text=str(rate))

    oled.show()
    return prev_t, new_t

def write_bf(start_t, e_count, dead_t):
    global buffer
    global sgn2
    
    #decalre global functions
    get_t_ms = utime.ticks_ms
    get_dt = utime.ticks_diff
    
    adc_val = 0
    while adc_val < 12000:
        adc_val = sgn2.read_u16()
    
    b_LED.on()
    e_count += 1
    dt = (get_dt(get_t_ms(), start_t))
    
    if dt<0:
        usys.exit()
    
    timestamp = rtc.datetime()
    timestring = "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3]+timestamp[4:7])
    
    deat_t = buffer.put([timestring, e_count, dt, adc_val, adc_val*1000, Temp, Pres, dead_t])
    
    b_LED.off()
    return e_count, dead_t

'''def read_bf():
    global buffer
    global oled
    #decalre global functions
    get_t_us = utime.ticks_us
    get_dt = utime.ticks_diff
    
    #print("1 is reading bf", bf_id)
    start_read_t = get_t_us()
    event = buffer.get(wait_routine=update_OLED, args=[oled, start_t, prev_t, new_t])
    with open("/sd/test01.txt", "a") as file:
        #write = file.write
        #for event in buffer[bf_id]:
        data = b"{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
        file.write(data)
            #usys.stdout.buffer.write(data)
    
    #print("1 has read bf", bf_id)
    #dt = (get_dt(get_t_us(), start_read_t) // 1000)
    #print("dt [ms]:", dt)'''

def core0_thread():
    global start_t
    global finished0
    global tot_events

    utime.sleep_ms(2000)
    start_t = utime.ticks_ms()
    
    e_count = 0
    cicles = 0

    dead_t = 0
    #while e_count < tot_events:
    while True:
        e_count, dead_t = write_bf(start_t, e_count, dead_t)
    
    finished0 = True
    print("0 finished", e_count)

def core1_thread():
    global start_t
    global finished0, finished1
    #global lock
    global Temp, Pres
    global tot_events
    global oled_id
    
    '''
    #I2C port
    i2c_dev, oled_id = OLED.init_i2c()

    #temperature sensor
    bmp = BMP280(i2c_dev)
    bmp.use_case(BMP280_CASE_INDOOR)

    Temp = bmp.temperature
    Pres = bmp.pressure

    #OLED display
    oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev, addr=addr_dict[name])
    oled.rotate(False)
    
    OLED.display_logo(oled) #Login screen
    
    #showing elapsed time
    OLED.display_text(oled, line=0, text="Thread:"+str(oled_id))
    #OLED.display_text(oled, line=0, start=58, text=str(oled_id))
    OLED.display_text(oled, line=0, start=70, text="Role:"+role)
    OLED.display_text(oled, line=1, text="Uptime:")
    OLED.display_text(oled, line=2, text="Count:")
    OLED.display_text(oled, line=3, text="Temp:")
    OLED.display_text(oled, line=4, text="Rate:")
    oled.rect(0,0,pix_res_x,pix_res_y,1)
    oled.show()
    '''
    
    with open("/sd/test01.txt", "w") as file:
        file.write("Comp_date  Comp_time\tEvent\tPico_time[ms]\tADC_value[0-65535]\tSiPM[mV]\tTemp[deg]\tPres[Pa]\tDeadtime[ms]\n")
    
    #decalre global functions
    #get_t_ms = utime.ticks_ms
    #get_dt = utime.ticks_diff
    
    prev_t = 0
    new_t = 0
    
    e_count = 0
    events = None
    #wait_r_results = [0, 0, 0, 0, 0]
    #while e_count < tot_events:
    while True:
        #if read_from == write_in:
            #display time while not reading
        #    prev_t, new_t = update_OLED(oled, start_t, prev_t, new_t)
        
        #elif read_from != write_in:
            #read buffer and save data
        #    read_bf((write_in+1)%2)
        #    read_from = write_in
        #start_read_t = get_t_ms()
        events, wait_r_results = buffer.get(wait_routine=update_OLED, args=[prev_t, new_t, e_count])
        e_count += len(events)
        prev_t = wait_r_results[0]
        new_t = wait_r_results[1]
        #print(event)
        with open("/sd/test01.txt", "a") as file:
            for event in events:
                data = b"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
                file.write(data)
            
    #if finished0:
    #    print(event)
    #    print("1 finished")
        #break
    
    #let core0 know we are done saving
    finished1 = True
    print("1 finished")
    #lock.release()

#create global lock
#lock = _thread.allocate_lock()

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

CoincidentMode()

#Core 1: timmer, buffer reader
core1 = _thread.start_new_thread(core1_thread, [])
#Core 0: data collection
core0_thread()

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