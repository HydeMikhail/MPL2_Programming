#! /usr/bin/env python3

'''
Utilities for MPL2 Programming Software
'''

import time
import os
import RPi.GPIO as gpio

def open_serial(device):
    '''
    Prevents the permissions to /dev/ttyS0 being
    blocked after closing and opening the port.
    '''
    os.system('sudo chmod a+rw /dev/ttyS0')
    device.open()

def start_seq(vdd, vpp, idleLedPin, statusPin):
    '''
    Applies power to VDD and pulls
    VPP to GND
    '''
    gpio.output(vpp, gpio.LOW)
    gpio.output(vdd, gpio.HIGH)
    gpio.output(idleLedPin, gpio.LOW)
    gpio.output(statusPin, gpio.HIGH)

def end_seq(vdd, vpp, idleLedPin, statusPin):
    '''
    Turns off power to VDD and
    resets VPP to HIGH
    '''
    gpio.output(vpp, gpio.HIGH)
    gpio.output(vdd, gpio.LOW)
    gpio.output(idleLedPin, gpio.HIGH)
    gpio.output(statusPin, gpio.LOW)

def error_ind(idleLedPin):
    '''
    Uses red LED to indicate if there
    was an error at any point. Blinks
    3 times and is passed as an exception
    to keep the program from terminating.
    '''
    for _ in range(5):
        gpio.output(idleLedPin, gpio.LOW)
        time.sleep(0.25)
        gpio.output(idleLedPin, gpio.HIGH)
        time.sleep(0.25)

def pass_ind(idleLedPin, statusPin, passPin):
    '''
    Activates Green LED to show the process has
    passed.
    '''
    gpio.output(idleLedPin, gpio.LOW)
    gpio.output(statusPin, gpio.LOW)
    gpio.output(passPin, gpio.HIGH)
    time.sleep(2)
    gpio.output(passPin, gpio.LOW)

def calc_set_point(roomTempReading):
    '''
    Takes the room temp reading from the pic
    and calculates the trip point based on
    the experimentally determined model.

    y = mx + b

    m = (room_temp - avg_offset) / room_temp_reading
    set_point = (trip_temp - avg_offset) / m

    Typical Room Temp = 25 C
    Trigger Temp = 72 C
    Average Offset = -671
    '''
    avgOffset = -671
    trigTemp = 72
    roomTemp = 25

    slope = (roomTemp - avgOffset) / roomTempReading
    return int((trigTemp - avgOffset) / slope)
