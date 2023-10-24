import utime
import _thread
import uos, sys
import gc  #garbage collector

sys.path.insert(1, r"/drivers/")
from ssd1306 import SSD1306_I2C
import sdcard

#modules
import OLED
import sd_module

#buffer to save data
buffer_size = 200
buffer = [[[0, 0, 0, 0]]*buffer_size, [[0, 0, 0, 0]]*buffer_size]
write_in = 0
read_from = 0
finished = False

def write_bf(sgn2, start_t, e_count, bf_id):
    global buffer
    global read_from
    
    #decalre global functions
    get_t_us = utime.ticks_us
    get_dt = utime.ticks_diff
    
    b_len = buffer_size
    b_index = 0
    
    print("0 is writting in bf", bf_id)
    while b_index < b_len:
        reading = sgn2.read_u16()
        dt = (get_dt(get_t_us(), start_t) // 1000)
        
        if reading > 1:
            e_count += 1
            buffer[bf_id][b_index] = [e_count, dt, reading]
            b_index += 1
    
    print(e_count)
    print("0 has written to bf", bf_id)
    return e_count

def read_bf(bf_id):
    global buffer
    
    print("1 is reading bf", bf_id)
    with open("/sd/test01.txt", "a") as file:
        write = file.write
        for event in buffer[bf_id]:
            data = "{}\t{}\t{}\n".format(*event)
            write(data)
        print("1 has read bf", bf_id)
    
def update_OLED(oled, start_t, prev_t, new_t):
    #decalre global functions
    get_t_ms = utime.ticks_ms
    get_dt = utime.ticks_diff
    
    new_t = (get_dt(get_t_ms(), start_t) // 1000) + 1
            
    if new_t > prev_t:        
        # Erase timer line
        OLED.erase_line(oled, line=4)
            
        OLED.display_text(oled, line=4, text=str(new_t))
        oled.show()
        
        prev_t = new_t
    return prev_t, new_t

def core0_thread():
    global finished
    global read_from, write_in
    
    #decalre global functions
    get_t_us = utime.ticks_us
    get_dt = utime.ticks_diff
    
    sgn2 = machine.ADC(26)
    ident = _thread.get_ident()
    
    tot_cicles = 10
    
    e_count = 0
    cicles = 0
    
    start_t = get_t_us()
    release_t = start_t
    while cicles < tot_cicles:
        #b_index = 0
        #waitflag=0 means we just check if we are free to use the lock
        #if lock.acquire(0):        
        e_count = write_bf(sgn2, start_t, e_count, write_in)
        
        write_in = (write_in+1)%2
        cicles += 1
    
    finished = True
    print("0 finished")

def core1_thread():
    global lock
    global finished
    global read_from, write_in
    
    #don't erase buffer before saving
    lock.acquire()
    
    #decalre global functions
    get_t_ms = utime.ticks_ms
    get_dt = utime.ticks_diff
    
    pix_res_x = 128
    pix_res_y = 64
    
    i2c_dev, ident = OLED.init_i2c()
    oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)
    
    oled.rotate(False)
    
    start_t = OLED.display_logo(oled) #Login screen
    
    #showing elapsed time
    OLED.display_text(oled, line=0, text="Thread")
    OLED.display_text(oled, line=1, text=str(ident))
    OLED.display_text(oled, line=3, text="Timer [s]:")
    oled.rect(0,0,pix_res_x,pix_res_y,1)
    oled.show()
    
    with open("/sd/test01.txt", "w") as file:
        file.write("#e_count\tt[ms]\tsignal2 [0, 65535]\n")
        
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