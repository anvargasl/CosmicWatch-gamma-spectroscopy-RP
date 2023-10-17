from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf, sys
import utime
import _thread

pix_res_x = 128
pix_res_y = 64

font_height = 8
margin = 5
spacing = 2 #space between lines

oled_dict = {0:{"scl":9, "sda":8}, 1:{"scl":27, "sda":26}}

def init_i2c(Id, scl_pin, sda_pin):
    # Initialize I2C device
    ident = str(_thread.get_ident())
    
    i2c_dev = I2C(Id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=200000)
    i2c_addr = [hex(ii) for ii in i2c_dev.scan()]
    
    if not i2c_addr:
        print(ident+' No I2C Display Found')
        sys.exit()
    else:
        print(ident+" I2C Address      : {}".format(i2c_addr)+"\n")
        print(ident+" I2C Configuration: {}".format(i2c_dev)+"\n")
    
    return i2c_dev, ident

def display_logo(oled):
    # Display the Raspberry Pi logo on the OLED
    buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)
    oled.fill(0)
    oled.blit(fb, 96, 0)
    oled.show()

def display_text(oled, line, text="Raspberry Pi"):
    # Display text on the OLED
    oled.text(text, margin, margin+line*(font_height+spacing))
    #oled.text("Pico", 5, 15)
    oled.show()
    
def display_timer(oled):
    # Display a simple timer animation on the OLED
    start_time = utime.ticks_ms()

    while True:
        elapsed_time = (utime.ticks_diff(utime.ticks_ms(), start_time) // 1000) + 1
        
        text_y = oled.height-font_height-margin
        
        # Clear the specific line by drawing a filled black rectangle
        width = oled.width-2*margin
        oled.fill_rect(margin, text_y, width, font_height, 0)

        oled.text("timer:", margin, text_y-font_height-spacing)
        oled.text(str(elapsed_time) + " sec", margin, text_y)
        oled.show()
        utime.sleep_ms(1000)
        
def display_counter(oled):
    # Display a simple timer animation on the OLED
    counter = 0
    while True:
        text_y = oled.height-font_height-margin
        
        # Clear the specific line by drawing a filled black rectangle
        width = oled.width-2*margin
        oled.fill_rect(margin, text_y, width, font_height, 0)

        oled.text("counter:", margin, text_y-font_height-spacing)
        oled.text(str(counter), margin, text_y)
        oled.show()
        utime.sleep_ms(2000)
        
        counter += 2

#display a timer or a even counter
def display_task(Id, task):
    '''if Id != 0 or Id != 1:
        print("valid Ids are 0 or 1")
        quit()
    if task != "timer" or task != "counter"
        print("valid tasks are \"timer\" or \"counter\"")
        quit()
    '''
    #global oled_dict
    i2c_dev, ident = init_i2c(Id=Id, scl_pin=oled_dict[Id]["scl"], sda_pin=oled_dict[Id]["sda"])
    oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)
    
    display_logo(oled)
    display_text(oled, line=0, text="Thread")
    display_text(oled, line=1, text=ident)
    oled.rect(0,0,pix_res_x,pix_res_y,1)
    oled.show()
    
    if task=="timer":
        display_timer(oled)
    elif task=="counter":
        display_counter(oled)

#MicroPython logo
'''
oled.fill(0)
oled.fill_rect(0, 0, 32, 32, 1)
oled.fill_rect(2, 2, 28, 28, 0)
oled.vline(9, 8, 22, 1)
oled.vline(16, 2, 22, 1)
oled.vline(23, 8, 22, 1)
oled.fill_rect(26, 24, 2, 4, 1)
'''