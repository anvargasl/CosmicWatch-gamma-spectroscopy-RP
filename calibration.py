import utime
import uos, usys
import machine

usys.path.insert(1, r"/drivers/")
#from ssd1306 import SSD1306_I2C
#from bmp280 import *
import sdcard

#modules
#import OLED

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

buffer_size = 10

#ADC pins
sgn2 = machine.ADC(26)
TriggerResetPin = machine.Pin(21, machine.Pin.OUT)

b_LED = machine.Pin(14, machine.Pin.OUT)

bkgd = 0
freq = 1 #Hz
period = int(1/freq)
print(period)

values = [0,0,0,0,0]
times = [0,0,0,0,0]

def write_bf(e_count, pulse_val, last_meas_t, file):
    global buffer
    global sgn2
    
    current_t = 0
    dt = 0
    temp = 0
    adc_val = sgn2.read_u16()
    while adc_val < bkgd+200:
        adc_val = sgn2.read_u16()
        temp = utime.ticks_us()
        dt = utime.ticks_diff(temp, last_meas_t)//1000000

        if dt > 3*period:
            print("signal at ground, continuing")
            return buffer_size, temp
        #if (current_t-last_meas_t)//1000 > 3*period:
        #    print("signal at ground, continuing 1")
        #    return buffer_size, utime.ticks_ms()
    
    #TriggerResetPin.on()
    #TriggerResetPin.off()
    
    values[1] = sgn2.read_u16()
    times[1] = utime.ticks_diff(utime.ticks_us(), temp)
    values[2] = sgn2.read_u16()
    times[2] = utime.ticks_diff(utime.ticks_us(), temp)
    values[3] = sgn2.read_u16()
    times[3] = utime.ticks_diff(utime.ticks_us(), temp)
    values[4] = sgn2.read_u16()
    times[4] = utime.ticks_diff(utime.ticks_us(), temp)
    values[0] = adc_val
    times[0] = temp
    
    b_LED.on()
    
    TriggerResetPin.on()
    TriggerResetPin.off()
    print(adc_val)
    
    #dt = (get_dt(get_t_ms(), start_t))
    
    #if dt<0:
    #    usys.exit()
    
    #timestamp = rtc.datetime()
    #timestring = "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3]+timestamp[4:7])
    
    event = [pulse_val, e_count, times[0], times[1], times[2], times[3], times[4], values[0], values[1], values[2], values[3], values[4]]
    data = b"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
    file.write(data)
    e_count += 1
    
    b_LED.off()
    return e_count, temp

def get_bkgd():
    global bkgd
    
    tot_meas = 10000
    temp = 0
    for i in range(0,tot_meas):
        temp += sgn2.read_u16()
        utime.sleep_us(1)
        
    bkgd = temp/tot_meas
    print("offset:", bkgd)
    
def calibrate():
    with open("/sd/calibration.txt", "w") as file:
        file.write("pulse_val, e_count, adc_val\n")
        
        dV = 20
        for p, pulse_val in enumerate(range(30, 231, dV)):
        #for p, pulse_val in enumerate([30,60,250]):
            
            e_count = 0
            print("measuring")
            last_meas_t = utime.ticks_us()
            while e_count < buffer_size:
                e_count, last_meas_t = write_bf(e_count, pulse_val, last_meas_t, file)
            
            print("change peak amplitude to "+str(pulse_val+dV))
            utime.sleep_ms(5000)

get_bkgd()
calibrate()
