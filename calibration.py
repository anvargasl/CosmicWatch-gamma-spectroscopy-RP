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

#--------------------setup ADC--------------------#
# Fetch single ADC sample
'''ADC_CHAN = 0
ADC_PIN  = 26 + ADC_CHAN

adc = devs.ADC_DEVICE
pin = devs.GPIO_PINS[ADC_PIN]
pad = devs.PAD_PINS[ADC_PIN]
pin.GPIO_CTRL_REG = devs.GPIO_FUNC_NULL
pad.PAD_REG = 0

adc.CS_REG = adc.FCS_REG = 0
adc.CS.EN = 1
adc.CS.AINSEL = ADC_CHAN
adc.CS.START_ONCE = 1
print(adc.RESULT_REG)

# Multiple ADC samples using DMA
DMA_CHAN = 0
NSAMPLES = 5 #buffer size
RATE = 10000 #samples per second
dma_chan = devs.DMA_CHANS[DMA_CHAN]
dma = devs.DMA_DEVICE

adc.FCS.EN = adc.FCS.DREQ_EN = 1
adc_buff = array.array('H', (0 for _ in range(NSAMPLES)))
adc.DIV_REG = (48000000 // RATE - 1) << 8
adc.FCS.THRESH = adc.FCS.OVER = adc.FCS.UNDER = 1

dma_chan.READ_ADDR_REG = devs.ADC_FIFO_ADDR
dma_chan.WRITE_ADDR_REG = uctypes.addressof(adc_buff)
dma_chan.TRANS_COUNT_REG = NSAMPLES

dma_chan.CTRL_TRIG_REG = 0
dma_chan.CTRL_TRIG.CHAIN_TO = DMA_CHAN
dma_chan.CTRL_TRIG.INCR_WRITE = dma_chan.CTRL_TRIG.IRQ_QUIET = 1
dma_chan.CTRL_TRIG.TREQ_SEL = devs.DREQ_ADC
dma_chan.CTRL_TRIG.DATA_SIZE = 1
dma_chan.CTRL_TRIG.EN = 1'''

# EOF

buffer_size = 100

#ADC pins
sgn2 = machine.ADC(26)
TriggerPin = machine.Pin(16, machine.Pin.IN)
TriggerResetPin = machine.Pin(21, machine.Pin.OUT)

b_LED = machine.Pin(14, machine.Pin.OUT)

bkgd = 0
freq = 1 #Hz
period = int(1/freq)
print("Period:", period)

interrupt_flag = 1
#values = [0,0,0,0,0]
#times = [0,0,0,0,0]

'''def get_bkgd():
    global bkgd
    
    tot_meas = 10000
    temp = 0
    for i in range(0,tot_meas):
        temp += sgn2.read_u16()
        utime.sleep_us(1)
        
    bkgd = temp/tot_meas
    print("offset:", bkgd)'''

readings = [None]*5 #apparently this declaration makes the saving faster in the interrupt
t_readings = [None]*2

def calibrate():
    global interrupt_flag
    
    with open("/sd/calibration.txt", "w") as file:
        file.write("pulse_val, e_count, adc_val\n")
        
        dV = 2
        last_meas_t = 0
        e_count = 0
        
        #print("measuring1")
        for p, pulse_val in enumerate(list(range(12, 41, dV))):
        #for p, pulse_val in enumerate([30,60,250]):
            
            print("measuring")
            last_meas_t = utime.ticks_us()
            e_count = 0
            interrupt_flag = 0
            
            while e_count < buffer_size:
                #print("int flag", interrupt_flag)

                if interrupt_flag:
                    #print("int flag", interrupt_flag)
                    
                    e_count += 1
                    last_meas_t = t_readings[0]
                    
                    event = [pulse_val, e_count]+t_readings+readings
                    data = b"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(*event)
                    file.write(data)
    
                    last_meas_t = t_readings[0]
    
                    b_LED.off()
                    
                    if e_count < buffer_size:
                        interrupt_flag = 0
                
                elif utime.ticks_diff(utime.ticks_us(), last_meas_t)//1000 > 5000:
                    print("not triggered, continuing")
                    continue
                    #print(interrupt_flag)
                
            print("change peak amplitude to "+str(pulse_val+dV))
            utime.sleep_ms(5000)

@micropython.native
def read_ADC(TriggerPin): #interrupt routine
    global interrupt_flag
    global readings
    global t_readings
    
    if interrupt_flag == 0:
        '''#data = [0,0]+[0]*NSAMPLES
        
        #TriggerResetPin.on()
        #TriggerResetPin.off()
        t_readings[0] = utime.ticks_us()
        #for i in range(NSAMPLES):
        adc.CS.START_ONCE = 1
        readings[0] = adc.RESULT_REG
        adc.CS.START_ONCE = 1
        readings[1] = adc.RESULT_REG
        adc.CS.START_ONCE = 1
        readings[2] = adc.RESULT_REG
        adc.CS.START_ONCE = 1
        readings[3] = adc.RESULT_REG
        adc.CS.START_ONCE = 1
        readings[4] = adc.RESULT_REG
        t_readings[1] = utime.ticks_us()
        
        TriggerResetPin.on()
        TriggerResetPin.off()
        
        t_readings[1] = utime.ticks_diff(t_readings[1], t_readings[0])
        b_LED.on()
        
        #print("triggered")
        interrupt_flag = 1'''
    
        '''t_readings[0] = utime.ticks_us()
        while adc.FCS.LEVEL:
            x = adc.FIFO_REG
        t_readings[1] = utime.ticks_diff(utime.ticks_us(), t_readings[0])
        
        adc.CS.START_MANY = 1
        while dma_chan.CTRL_TRIG.BUSY:
            time.sleep_ms(10)
        adc.CS.START_MANY = 0
        dma_chan.CTRL_TRIG.EN = 0
        t_readings[2] = utime.ticks_diff(utime.ticks_us(), t_readings[1])
        readings = adc_buff
        #print(vals)
        
        TriggerResetPin.on()
        TriggerResetPin.off()
        
        b_LED.on()
        
        print("triggered")
        interrupt_flag = 1'''
        
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

#print(machine.Pin.__dict__.keys())
#get_bkgd()
calibrate()
