import utime
import _thread
import uos, sys

sys.path.insert(1, r"/drivers/")
from ssd1306 import SSD1306_I2C
import sdcard

#modules
import OLED
import sd_module

#buffer to save data
buffer = [[0, 0, 0, 0]]*200
finished = False

def core0_thread():
    global lock, buffer, finished
    
    sgn2 = machine.ADC(26)
    ident = str(_thread.get_ident())
    
    counter = 0
    
    b_len = len(buffer)
    print("buffer size:", b_len)
    tot_cicles = 5
    tot_events = b_len*tot_cicles
    b_index = 0
    e_count = 0
    
    cicles = 0
    
    start_t = utime.ticks_us()
    printed = 0
    while cicles < tot_cicles:
        #waitflag=0 means we just check if we are free to use the lock
        if lock.acquire(0):
            print("0 got the lock")
            while b_index < b_len:
        
                reading = sgn2.read_u16()
                dt = (utime.ticks_diff(utime.ticks_us(), start_t) // 1000)
                
                if reading > 1:
                    e_count += 1
                    
                    buffer[b_index] = [ident, e_count, dt, reading]
                    b_index += 1
                    print(e_count)
            
                if b_index == b_len:
                    lock.release()
                    print("0 released the lock")
                    utime.sleep_ms(10)
                    cicles += 1
                    printed = 0
                
            b_index = 0
        else:
            if printed == 0:
                print("0 waiting fot the lock")
                printed = 1
            
    lock.acquire()
    finished = True
    print("finished")

def core1_thread():
    global lock, buffer, finished
    
    pix_res_x = 128
    pix_res_y = 64
    
    i2c_dev, ident = OLED.init_i2c()
    oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)
    
    oled.rotate(False)
    
    start_t = OLED.display_logo(oled) #Login screen
    
    #showing elapsed time
    OLED.display_text(oled, line=0, text="Thread")
    OLED.display_text(oled, line=1, text=ident)
    OLED.display_text(oled, line=3, text="Timer:")
    oled.rect(0,0,pix_res_x,pix_res_y,1)
    oled.show()
    
    with open("/sd/test01.txt", "w") as file:
        file.write("#ident\tcounter\tt[ms]\tsignal2 [0, 65535]\n")
        
    prev_elapsed_t = 0
    new_elapsed_t = 0
    
    while True:
        #waitflag=0 means we just check if we are free to use the lock
        if not lock.acquire(0):
            #print("1 WAITING FOR THE LOCK")
            new_elapsed_t = (utime.ticks_diff(utime.ticks_ms(), start_t) // 1000) + 1
            
            if new_elapsed_t > prev_elapsed_t:        
                # Erase timer line
                OLED.erase_line(oled, line=4)
                
                OLED.display_text(oled, line=4, text=str(new_elapsed_t)+ " sec")
                oled.show()
                
                prev_elapsed_t = new_elapsed_t
        else:
            print("1 got the lock")
            with open("/sd/test01.txt", "a") as file:
                for event in buffer:
                    data = "{}\t{}\t{}\t{}\n".format(*event)
                    file.write(data)
            
            lock.release() #let core0 write in the buffer
            print("1 released the lock")
            utime.sleep_ms(10)
            if finished:
                return

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

#CosmicWatch  OLED configuration
core1 = _thread.start_new_thread(core1_thread, [])
core0_thread()

with open("/sd/test01.txt", "r") as file:
    data = file.read()
    print(data)