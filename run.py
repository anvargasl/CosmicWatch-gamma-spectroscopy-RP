import utime
import _thread
import uos, usys
import gc  #garbage collector
import random as rand
import machine

usys.path.insert(1, r"/drivers/")
from ssd1306 import SSD1306_I2C
import sdcard

#modules
import OLED
import sd_module

#global start time
start_t = utime.ticks_us()
rtc = machine.RTC()

#ADC pins
sgn2 = machine.ADC(26)

#buffer to save data
buffer_size = 200
buffer = [[[0,0,0,0,0,0,0]]*buffer_size, [[0,0,0,0,0,0,0]]*buffer_size]
write_in = 0
read_from = 0
finished = False

def update_OLED(oled, timer_start_t, prev_t, new_t):
    
    new_t = (utime.ticks_diff(utime.ticks_us(), timer_start_t) // 1000000) + 1
            
    if new_t > prev_t:
        # Erase timer line
        OLED.erase_line(oled, line=4)
            
        OLED.display_text(oled, line=4, text=str(new_t))
        oled.show()
        
        prev_t = new_t
    return prev_t, new_t

def write_bf(start_t, e_count, bf_id):
    global buffer
    global sgn2
    global read_from
    
    #decalre global functions
    get_t_us = utime.ticks_us
    get_dt = utime.ticks_diff
    
    b_len = buffer_size
    b_index = 0
    
    #print("0 is writting in bf", bf_id)
    start_write_t = get_t_us()
    
    while b_index < b_len:
        reading = sgn2.read_u16()
        
        if reading > 1:
            e_count += 1
            dt = (get_dt(get_t_us(), start_t) // 1000)
            
            timestamp = rtc.datetime()
            timestring = "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3]+timestamp[4:7])
            
            temp = rand.randint(0, 100)
            dead_t = rand.randint(0, 200)
            
            buffer[bf_id][b_index] = [timestring, e_count, dt, reading, reading*1000, temp, dead_t]
            b_index += 1
    
    #print(e_count)
    #print("0 has written to bf", bf_id)
    dt = (get_dt(get_t_us(), start_write_t) // 1000)
    print("aqct [ms]:", dt)
    return e_count

def read_bf(bf_id):
    global buffer
    #decalre global functions
    get_t_us = utime.ticks_us
    get_dt = utime.ticks_diff
    
    #print("1 is reading bf", bf_id)
    start_read_t = get_t_us()
    
    with open("/sd/test01.txt", "a") as file:
        write = file.write
        for event in buffer[bf_id]:
            data = b"{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
            write(data)
            #usys.stdout.buffer.write(data)
    
    #print("1 has read bf", bf_id)
    dt = (get_dt(get_t_us(), start_read_t) // 1000)
    print("dt [ms]:", dt)

def core0_thread():
    global start_t
    global finished
    global read_from, write_in
    
    #ident = _thread.get_ident()
    
    tot_cicles = 3
    
    e_count = 0
    cicles = 0
    
    while cicles < tot_cicles:     
        e_count = write_bf(start_t, e_count, write_in)
        
        write_in = (write_in+1)%2
        cicles += 1
    
    finished = True
    print("0 finished")

def core1_thread():
    global start_t
    global lock
    global finished
    global read_from, write_in
    
    #don't erase buffer before saving
    lock.acquire()
    
    pix_res_x = 128
    pix_res_y = 64
    
    #timer start time
    #timer_start_t = start_t//1000
    
    i2c_dev, ident = OLED.init_i2c()
    oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)
    
    oled.rotate(False)
    
    OLED.display_logo(oled) #Login screen
    
    #showing elapsed time
    OLED.display_text(oled, line=0, text="Thread")
    OLED.display_text(oled, line=1, text=str(ident))
    OLED.display_text(oled, line=3, text="Timer [s]:")
    oled.rect(0,0,pix_res_x,pix_res_y,1)
    oled.show()
    
    with open("/sd/test01.txt", "w") as file:
        file.write("Comp_date  Comp_time\tEvent\tPico_time[ms]\tADC_value[0-65535]\tSiPM[mV]\tDeadtime[ms]\n")
        
    prev_t = 0
    new_t = 0
    
    while True:
        if read_from == write_in:
            #display time while not reading
            prev_t, new_t = update_OLED(oled, start_t, prev_t, new_t)
        
        elif read_from != write_in:
            #read buffer and save data
            read_bf((write_in+1)%2)
            read_from = write_in
            
            if finished:
                print("1 finished")
                break
    
    #let core0 know we are done saving
    lock.release()

#create global lock
lock = _thread.allocate_lock()

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
core0_thread()

#Wait for core1 to be done before erasing buffer and printing to screen
lock.acquire()
#erase buffer
buffer = None
gc.collect()

print("done")
with open("/sd/test01.txt", "r") as file:
    print(file.read())