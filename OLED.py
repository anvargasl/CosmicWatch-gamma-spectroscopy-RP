#OLED

from machine import Pin, I2C
import framebuf, sys
import utime
import _thread

pix_res_x = 128
pix_res_y = 64

font_height = 8
margin = 2
spacing = 2 #space between lines

def init_i2c():
    # Initialize I2C device
    ident = _thread.get_ident()
    
    i2c_dev = I2C(0, scl=Pin(13), sda=Pin(12), freq=200000)
    i2c_addr = [hex(ii) for ii in i2c_dev.scan()]
    
    if not i2c_addr:
        print(str(ident)+' No I2C Display Found')
        sys.exit()
    else:
        print(str(ident)+" I2C Address      : {}".format(i2c_addr)+"\n")
        print(str(ident)+" I2C Configuration: {}".format(i2c_dev)+"\n")
    
    return i2c_dev, ident

def display_logo(oled):
    # Display the CosmicWatch logo on the entire OLED
    buffer = bytearray(b"BM>\x04\x00\x00\x00\x00\x00\x00>\x00\x00\x00(\x00\x00\x00\x80\x00\x00\x00@\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x04\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc1\xc0\xf0\x1c\x07|\x06\x07\x00\x00\x00\x00\x00\x00\x00\x01\xc1\xc1\xf8>\x07\xfe\x06\x07\x00\x00\x00\x00\x00\x00\x00\x01\xc1\xc3\xfe\x7f\x07\xce\x0f\x0f\x80\x00\x00\x00\x00\x00\x00\x01\xc1\xc7\x1f'\x07\x8e\x0f\x0f\x80\x00\x00\x00\x00\x00\x00\x01\xc1\xc6\x0f\x07\x07\x1e\x1f\x0f\xc0\x00\x00\x00\x00\x00\x00\x01\xc1\xc4\x07\x07\x07<\x1f\x9f\xc0\x00\x00\x00\x00\x00\x00\x01\xc1\xc0\x07\x07\x07\xf8\x1f\x9f\xc0\x00\x00\x00\x00\x00\x00\x01\xc1\xc0\x07\x07\x07\xe09\x99\xe0\x00\x00\x00\x00\x00\x00\x01\xc3\xc3\x07\x07\x07\x8c9\xf9\xe0\x00\x00\x00\x00\x00\x00\x01\xe7\xc7\x8f\x07\x07\x0e9\xf9\xe0\x00\x00\x00\x00\x00\x00\x01\xff\xc7\x8e\x07\x07\x1ep\xf0\xf0\x00\x00\x00\x00\x00\x00\x00\xff\xc3\x9c?\xe3\xfcp\xf0\xf0\x00\x00\x00\x00\x00\x00\x00}\xc1\xf0?\xe1\xf8p\xf0\xf0\x00\x00\x00\x00\x00\x00\x00\x01\xc0\x00\x07\x80\x00\xe0`x\x00\x00\x00\x00\x00\x00\x00\x01\xc0\x00\x07\x00\x00\xe0`x\x00\x00\x00\x00\x00\x00\x00\x01\xc0\x00\x06\x00\x00\xe0`x\x00\x00\x00\x01\x00\x00\x00\x01\xc0\x00\x04\x00\x01\xc0@<\x00\x00\x00\x03\xff\x80\x00\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x81\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xf0 \x00\x00\x00\x00x\x0e\x1c<8>\x00\xe0\x0f\x03\xf8\x7f\x80\x00\x00\x00\xfc\x0e\x1c<8\x7f\x03\xf8\x1c \xfc \x00\x00\x00\x01\xff\x0e\x1c<8\xf7\x8f\xbe8`~\x00\x00\x00\x00\x03\x8f\x8e\x1c<8\xe1\x8f\x1e0`>\x08\x00\x00\x00\x03\x07\x8e\x1c<8\xe0\x1f\x1f\x00\xf0\x1f\x1f\x80\x00\x00\x02\x03\x8e\x1c<8\xf8\x1e\x0f\x00\xf8\x1f\x08\x00\x00\x00\x00\x03\x8e\x1c<8|\x1e\x0f\x00\xfc\x0f\x00\x00\x00\x00\x00\x03\x8e\x1c<8?\x1e\x0f\x00:\x0f\x04\x00\x00\x00\x01\x83\x8e\x1c<8\x0f\x9e\x0f\x00\x11\x8f\x0f\x80\x00\x00\x03\xc7\x8e\x1c<8\x03\x9f\x1f\x00\x00\xcf\x04\x00\x00\x00\x03\xc7\x0e\x1e\xfe\xf8\xc3\x8f\x1e\x00\x00\xef\x00\x00\x00\x00\x01\xce\x0e\x1f\xff\xf8\xe7\x0f\xbe\x00\x03\xef\x08\x00\x00\x00\x00\xf8\x0e\x0f\xcf\xb8~\x03\xf8\x10\x07\xdf\x1f\x80\x00\x00\x00\x00\x00\x07\x878<\x00\xe0\x08\x0f\xde\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000?\xbe\x00\x00\x00\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x0083| \x00\x00\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x1c<\xf8\x7f\x80\x00\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x0f\x03\xf0 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\x81\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    buffer = bytearray([buffer[ii] for ii in range(len(buffer)-1,-1,-1)]) #delete this line for RP logo
    
    img_xsize = 128
    img_ysize = 64
    
    fb = framebuf.FrameBuffer(buffer, img_xsize, img_ysize, framebuf.MONO_HMSB)
    oled.fill(0) #clear screen
    oled.blit(fb, 0, 0) #draw
    oled.show()
    
    #start_t = utime.ticks_ms()
    utime.sleep_ms(2000)
    oled.fill(0) #clear screen

def display_text(oled, line, start=margin, text="Raspberry Pi"):
    #display text on the OLED
    oled.text(text, start, margin+line*(font_height+spacing))
    oled.show()
    
def erase_line(oled, line, start=margin, end=pix_res_x-margin):
    #draw a black box over line to be erased
    width = end-start
    oled.fill_rect(start, margin+line*(font_height+spacing), width, font_height, 0)
    oled.show()
    
def erase_lines(oled, lines=[0,1], start=margin, end=pix_res_x-margin):
    #draw a black box over line to be erased
    width = end-start
    height = (lines[-1]+1-lines[0])*(font_height+spacing)
    oled.fill_rect(start, margin+lines[0]*(font_height+spacing), width, height, 0)
    oled.show()
    
def display_timer(oled):
    #display a simple timer animation on the OLED
    
    text_y = oled.height-font_height-margin
    width = oled.width-2*margin
    
    start_time = utime.ticks_ms()
    while True:
        elapsed_time = (utime.ticks_diff(utime.ticks_ms(), start_time) // 1000) + 1
        
        # Clear the specific line by drawing a filled black rectangle
        oled.fill_rect(margin, text_y, width, font_height, 0)

        oled.text("Uptime:", margin, text_y-font_height-spacing)
        oled.text(str(elapsed_time) + " sec", margin, text_y)
        oled.show()
        
        utime.sleep_ms(1000)
             
def display_counter(oled):
    #display a simple even number counter animation on the OLED
    text_y = oled.height-font_height-margin
    width = oled.width-2*margin
    
    erase = oled.fill_rect
    write = oled.text
    wait = utime.sleep_ms
    
    counter = 0
    while True:
        #clear the specific line by drawing a filled black rectangle
        erase(margin, text_y, width, font_height, 0)
        write("counter:", margin, text_y-font_height-spacing)
        write(str(counter), margin, text_y)
        oled.show()
        wait(1000)
        
        counter += 2
                
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
#RP logo
#b'BM>\x02\x00\x00\x00\x00\x00\x00>\x00\x00\x00(\x00\x00\x00@\x00\x00\x00@\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x02\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x00\x18`\x00\x00\x00\x00\x00\x07\xff\xff\xc0\x00\x00\x00\x00\x07\xff\xff\xc0\x00\x00\x00\x00\x07\xff\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x00\x00\xff\xfe\x00\x00\x00\x00\x0f\xfe\xff\xfe\x00\x00\x00\x00\x1f\xfe\xff\xfe\xff\xf8\x00\x00\x1f\xfe\x7f\xfc\xff\xf8\x00\x00\x00\x00\x7f\xfc\x00\x00\x00\x00\x00\x00?\xf8\x00\x00\x00\x00\x00\x00\x1f\xf0\x00\x00\x00\x00\x00\x00\xcf\xe0\x00\x00\x00\x00\x00\x01\xc1\x82\x00\x00\x00\x00\x00\x03\x81\x87\x00\x00\x00\x00\x00\x07\x01\x83\x80\x00\x00\x00\x00\x0e\x01\x81\xc0\x00\x00\x00\x00\x1c\x01\x80\xe0\x00\x00\x00\x008\x01\x80p\x00\x00\x00\x00p\x01\x808\x00\x00\x00\x00\xe0\x01\x80\x1c\x00\x00\x00\x00\x00\x01\x80\x0e\x00\x00\x00\x00\x00\x01\x80\x06\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00'