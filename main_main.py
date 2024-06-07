#main.py

import utime
import uos, usys
import machine
from array import array

usys.path.insert(1, r"/drivers/")
import sdcard

#--------------------setup SD card--------------------#
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

#ADC pins
sgn2 = machine.ADC(26)
TriggerPin = machine.Pin(16, machine.Pin.IN)
TriggerResetPin = machine.Pin(21, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN)

b_LED = machine.Pin(14, machine.Pin.OUT)

bkgd = 0
interrupt_flag = 1

readings = [None]*5 #apparently this declaration makes the saving faster in the interrupt
t_readings = [None]*2
def calibrate():
    with open("/sd/calibration.txt", "w") as file:
        file.write("pulse_val, e_count, adc_val\n")
        interrupt_flag = 0
        
        e_count = 0

        while True:
            #print("int flag", interrupt_flag)
            
            if interrupt_flag:
                e_count += 1
                
                event = [e_count]+list(t_readings+readings)
                data = b"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
                #print("saving")
                file.write(data)
                
                if e_count // 100 == 0:
                    file.flush()

                b_LED.off()
                
                interrupt_flag = 0

def calibrate_flush():
    global interrupt_flag
    
    with open("/sd/calibration.txt", "w") as file:
        file.write("pulse_val, e_count, adc_val\n")
        interrupt_flag = 0
        
        e_count = 0

        while True:
            #print("int flag", interrupt_flag)
            
            if interrupt_flag:
                e_count += 1
                
                event = [e_count]+list(t_readings+readings)
                data = b"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
                #print("saving")
                file.write(data)
                
                if e_count // 100 == 0:
                    file.flush()

                b_LED.off()
                
                interrupt_flag = 0

@micropython.native
def read_ADC(TriggerPin): #interrupt routine
    global interrupt_flag
    global readings
    global t_readings
    
    if interrupt_flag == 0:
        
        t_readings[0] = utime.ticks_us()
        
        readings[0] = sgn2.read_u16() #this seems slightly better than saving the global function
        readings[1] = sgn2.read_u16()
        readings[2] = sgn2.read_u16()
        readings[3] = sgn2.read_u16()
        readings[4] = sgn2.read_u16()
        
        t_readings[1] = utime.ticks_diff(utime.ticks_us(), t_readings[0])
        
        TriggerResetPin.on()
        TriggerResetPin.off()
        
        b_LED.on()
        
        #print("triggered")
        interrupt_flag = 1
    
TriggerPin.irq(trigger=machine.Pin.IRQ_RISING, handler=read_ADC)

#calibrate()
calibrate_flush()