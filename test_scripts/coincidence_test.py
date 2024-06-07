import machine
import utime
import uos, usys

usys.path.insert(1, r"/drivers/")
from ssd1306 import SSD1306_I2C

#modules
import OLED

addr_dict = {"blue": 0x3D, "green": 0x3C}
name = "green"

COINCIDENCE = None
coincident_= signal_input_pin  = None
coincident_signal_output_pin = None

b_LED = machine.Pin(14, machine.Pin.OUT)
s_LED = machine.Pin(15, machine.Pin.OUT)

#OLED
oled_id = None
pix_res_x = 128
pix_res_y = 64

b_LED.on()
s_LED.on()
utime.sleep_ms(1000)
b_LED.off()
s_LED.off()

#I2C port
i2c_dev, oled_id = OLED.init_i2c()

#OLED display
oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev, addr=addr_dict[name])
oled.rotate(False)

oled.fill(0) #clear screen

OLED.display_text(oled, line=0, text=name+" searching")

def CoincidentMode():
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
        OLED.erase_line(oled, line=0)
        OLED.display_text(oled, line=0, text="S")
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
                OLED.erase_line(oled, line=0)
                OLED.display_text(oled, line=0, text="M")
                
                return
            
            utime.sleep_ms(10)
        
        coincident_pin_1.off()
        OLED.erase_line(oled, line=0)
        OLED.display_text(oled, line=0, text="No partner")
        utime.sleep_ms(3000)
        OLED.erase_line(oled, line=0)
        OLED.display_text(oled, line=0, text="M")
        

CoincidentMode()