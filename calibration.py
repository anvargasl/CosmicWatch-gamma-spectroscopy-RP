#calibration.py

import utime
import uos, usys
import machine

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
TriggerResetPin = machine.Pin(21, machine.Pin.OUT)

b_LED = machine.Pin(14, machine.Pin.OUT)

#interrupt only when data is not being saved
interrupt_flag = 1

#apparently this declaration makes the saving faster in the interrupt
readings = [None]*5   #5 measurements are done for each pulse
t_readings = [None]*2 #Trigger and end of measurement time
buffer_size = 100     #Number of trigger events to be saved per simulated pulse

def calibrate():
    global interrupt_flag
    
    with open("/sd/calibration.txt", "w") as file:
        file.write("pulse_val,e_count,t0[us],dt0[us],readings\n")
        
        last_meas_t = 0 #last measurement time
        e_count = 0 #Trigger event count
        
        ''' The peak detected signal does not increase linearly with respect to the SiPM pulses,
            therefore, a lower resolution dV2>dV1 is used in order to get appreciable changes'''
        dV1 = 2
        dV2 = 10
        #List of artificial SiPM-pulse maxima
        Voltages = list(range(12, 41, dV1))+list(range(50, 251, dV2))
        
        for p, pulse_val in enumerate(Voltages):
            
            #set input pulse amplitude
            print("set peak amplitude to "+str(Voltages[p])+" mV")
            utime.sleep_ms(5000)
            
            print("measuring")
            last_meas_t = utime.ticks_us()
            
            e_count = 0 #reset event count
            interrupt_flag = 0 #allow interruptions
            
            while e_count < buffer_size:
                
                #save collected data
                if interrupt_flag:
                    
                    e_count += 1 #increase event count
                    
                    event = [pulse_val, e_count]+t_readings+readings
                    data = b"{},{},{},{},{},{},{},{},{}\n".format(*event)
                    file.write(data)
    
                    last_meas_t = t_readings[0]
    
                    b_LED.off()
                    
                    if e_count < buffer_size:
                        interrupt_flag = 0 #allow interrupts
                
                #continue to next pulse value if not triggered after 5 seconds from last measurement
                elif utime.ticks_diff(utime.ticks_us(), last_meas_t)//1000 > 5000:
                    print("not triggered, continuing")
                    break

@micropython.native #python decorator for a faster routine
def read_ADC(TriggerPin): #interrupt routine, only 
    global interrupt_flag
    global readings
    global t_readings
    
    if interrupt_flag == 0:
        
        t0 = utime.ticks_us() #trigger time
        
        #read peak detection
        readings[0] = sgn2.read_u16()
        readings[1] = sgn2.read_u16()
        readings[2] = sgn2.read_u16()
        readings[3] = sgn2.read_u16()
        readings[4] = sgn2.read_u16()
        
        dt0 = utime.ticks_diff(utime.ticks_us(), t0) #time elapsed from t0
        t_readings[0] = t0
        t_readings[1] = dt0
        
        TriggerResetPin.on() #Discharge Peak-detector capacitor
        TriggerResetPin.off()
        
        b_LED.on()
        
        interrupt_flag = 1 #signal trigger event
    
TriggerPin.irq(trigger=machine.Pin.IRQ_RISING, handler=read_ADC) #declare interrup routine

calibrate() #start calibration
