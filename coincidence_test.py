import machine
import utime

COINCIDENCE = None
coincident_= signal_input_pin  = None
coincident_signal_output_pin = None

b_LED = machine.Pin(14, machine.Pin.OUT)
s_LED = machine.Pin(15, machine.Pin.OUT)

def CoincidentMode():
    global COINCIDENCE
    global coincident_signal_input_pin
    global coincident_signal_output_pin
    
    coincident_pin_1 = machine.Pin(19, machine.Pin.IN)
    coincident_pin_2 = None
    
    #if someone is talking to me in channel 1, then talk in chanel 2
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
        print("Coincidence detector found.")
        utime.sleep_ms(1000)

    else: #if nobody is talking to me in channel 1, then talk in channel 1
        coincident_pin_1 = machine.Pin(19, machine.Pin.OUT)
        coincident_pin_1.on()
        coincident_pin_2 = machine.Pin(20, machine.Pin.IN)
        #filename[4] = ‘M’; // Label the filename as “M”aster
        utime.sleep_ms(2000)
        for i in range(0,101):
            utime.sleep_ms(10)
        
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
                print("Coincidence detector found.")
                break
