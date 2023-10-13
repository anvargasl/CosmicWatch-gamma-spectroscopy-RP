# CosmicWatch_V3_RP

This repository contains all the necesary codes to upload to the Raspberry Pi board for data acquisition, display, gps, sensor usage and others. All the code is built using [MycroPython](https://micropython.org/)

## Structure

**led.py** contains a basic example to blink the RP Pico built in LED.

**OLED.py** contains some example functions to display text and images on the OLED while using the [ssd1306.py](https://github.com/micropython/micropython/blob/bc7822d8e95c40a9d5e403fd22c82b1bbad53b8b/drivers/display/ssd1306.py) driver.

**RPI_PICO-20220618-v1.19.1.uf2** contains the latest version of **MicroPython** that worked with the OLED library **ssd1306.py**. Version .20 and .21 have shown some trouble while using **Thonny** and **ssd1306.py**.

### headers

### source
