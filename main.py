from ssd1306 import SSD1306_I2C
from utime import sleep
import OLED
import _thread

pix_res_x = 128
pix_res_y = 64

def main():
    i2c_dev0 = OLED.init_i2c(Id=0, scl_pin=9, sda_pin=8)
    i2c_dev1 = OLED.init_i2c(Id=1, scl_pin=27, sda_pin=26)
    oled0 = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev0)
    oled1 = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev1)
    
    OLED.display_logo(oled1)
    oled1.rect(0,0,128,64,1)
    oled1.show()
    
    OLED.display_text(oled0, text="\n Magnolia")
    OLED.display_anima(oled0)

if __name__ == '__main__':
    main()
