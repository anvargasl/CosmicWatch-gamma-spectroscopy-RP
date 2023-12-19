#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# vim:fileencoding=UTF-8:ts=4

from array import array
from machine import ADC
from time import ticks_ms, ticks_diff, sleep_ms
import rp_devices

from math import sqrt, pow

def measure(data):
    index = 0
    adc = machine.ADC(26)
    f = adc.read_u16
    t0 = ticks_ms()
    while index < NUM:
        data[index] = f()
        index += 1
    t1 = ticks_ms()
    td_µs = ticks_diff(t1, t0) * 1e3
    print(f'{td_µs/NUM:6.2f} µs/conversion   {1e6/td_µs*NUM:6.0f} sps')
    sleep_ms(20)

@micropython.native
def measure_native(data):
    index = 0
    adc = machine.ADC(26)
    f = adc.read_u16
    t0 = ticks_ms()
    while index < NUM:
        data[index] = f()
        index += 1
    t1 = ticks_ms()
    td_µs = ticks_diff(t1, t0) * 1e3
    print(f'{td_µs/NUM:6.2f} µs/conversion   {1e6/td_µs*NUM:6.0f} sps')
    sleep_ms(20)

@micropython.viper
def measure_viper(data):
    d: ptr16 = ptr16(data)
    _num: int = int(NUM)
    index: int = 0
    adc = machine.ADC(26)
    f = adc.read_u16
    t0: int = ticks_ms()
    while index < _num:
        d[index] = int(f())
        index += 1
    t1: int = ticks_ms()
    td_µs = ticks_diff(t1, t0) * 1e3
    print(f'{td_µs/NUM:6.2f} µs/conversion   {1e6/td_µs*NUM:6.0f} sps')
    sleep_ms(20)
    
@micropython.viper
def get_sample(data:ptr):
    d: ptr16 = ptr16(data)
    _num: int = int(NUM)
    index: int = 0
    adc = machine.ADC(26)
    f = adc.read_u16
    t0: int = ticks_ms()
    while index < _num:
        d[index] = int(f())
        index += 1
    t1: int = ticks_ms()
    td_us = ticks_diff(t1, t0) * 1e3
    print(d[1])
    print(f'{td_us/NUM:6.2f} µs/conversion   {1e6/td_us*NUM:6.0f} sps')
    sleep_ms(20)
    
    return d, td_us

NUM = const(10_000)
data1 = array('H', (0 for _ in range(NUM)))

iterations = const(10)
repetitions = const(100)

mean = [0]*iterations
sdev = [0]*iterations
times = [0]*iterations
def get_statistics(i):
    global mean, sdev
    global data1
    
    print("here")
    print(data1)
    mean[i] = sum(data1)/repetitions
    sdev[i] = sqrt(sum([(t-mean[i])**2 for t in data1])/repetitions)
    
    print(mean)
    print(sdev)

def get_bkgd():
    global data1
    
    for i in range(iterations):
        print(data1)
        data1, td_us = get_sample(data1)
        print(data1)
        get_statistics(i)
    utime.sleep_ms(1)

data = array('H', (0 for _ in range(NUM)))
print('start')
measure(data)
measure_native(data)
measure_viper(data)

get_bkgd()
print(data)
print(td_us)
#get_bkgd()
