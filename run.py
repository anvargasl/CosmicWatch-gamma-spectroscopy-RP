import utime
import _thread
import uos, sys

sys.path.insert(1, r"/drivers/")
import sdcard

#modules
import OLED
import sd_module

#Id = 0 :CosmicWatch  OLED configuration
new_thread = _thread.start_new_thread(OLED.display_task, ["timer"])

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

def run_multi_thread():
    
    sgn2 = machine.ADC(26)
    ident = str(_thread.get_ident())
    
    counter = 0
    
    #buffer = 
    
    with open("/sd/test01.txt", "w") as file:
        file.write("#ident\tcounter\tt[ms]\tsignal2 [0, 65535]\n")
        start_time = utime.ticks_us()
        
        while counter < 100:
            reading = sgn2.read_u16()
            dt = (utime.ticks_diff(utime.ticks_us(), start_time) // 1000)
            
            if reading > 1:
                counter += 1
                file.write(f"{ident}\t{counter}\t{dt}\t{reading}\n")

if __name__ == '__main__':
    run_multi_thread()
