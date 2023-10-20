# CosmicWatch_V3_RP

This repository contains all the necesary codes to upload to the Raspberry Pi board for data acquisition, display, gps, sensor usage and others. All the code is built using [MycroPython](https://github.com/micropython)

## Structure

### OLED.py
contains some example functions to display text and images on the OLED while using the [ssd1306.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py) driver.

**RPI_PICO-20220618-v1.19.1.uf2** contains the latest version of **MicroPython** that worked with the OLED library **ssd1306.py**. Version .20 and .21 have shown some trouble while using **Thonny** and **ssd1306.py**.

**led.py** contains a basic example to blink the RP Pico built in LED.

## Logos

Contains a 128x64 pixel Cosmic watch logo, converted into a bytearray for display on the OLED by running the **png_to_bytearray.py** script found in this [GitHub repo](https://github.com/makerportal/rpi-pico-ssd1306/blob/main/python3/png_to_bytearray.py). The resulting bytearray is then displayed on the OLED by means of the **display_logo** method of the [OLED.py](#oled-py) module.

Such images can be created by resizng png files to the desired pixel resolution and refining them with pixel art software as [Pixilart](https://www.pixilart.com/).
