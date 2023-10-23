# CosmicWatch_V3_RP

This repository contains all the necesary codes to upload to the Raspberry Pi board for data acquisition, display, gps, sensor usage and others. All the code is built using [MycroPython](https://github.com/micropython)

## Libraries

[Awesome MicroPython](https://awesome-micropython.com/) is a good first try to find libraries for the different components used by CosmicWatch.

## Structure

### OLED.py
contains some example functions to display text and images on the OLED while using the [ssd1306.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py) driver.

**RPI_PICO_W-20231005-v1.21.0.uf2** contains the latest version of **MicroPython** used for testing the CosmicWatch with a RapberryPi Pico W. For a RaspberryPi Pico **RPI_PICO-20220618-v1.19.1.uf2**nseems to be the version that works best with the **ssd1306.py** library, versions .20 and .21 have shown some trouble while using **Thonny**.

**led.py** contains a basic example to blink the RP Pico built in LED.

## Logos

Contains a 128x64 pixel Cosmic watch logo, converted into a bytearray for display on the OLED by running the **png_to_bytearray.py** script found in this [GitHub repo](https://github.com/makerportal/rpi-pico-ssd1306/blob/main/python3/png_to_bytearray.py). The resulting bytearray is then displayed on the OLED by means of the **display_logo** method of the [OLED.py](#oled-py) module.

Such images can be created by resizng png files to the desired pixel resolution and refining them with pixel art software as [Pixilart](https://www.pixilart.com/).
