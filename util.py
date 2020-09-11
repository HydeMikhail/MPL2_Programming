#! /usr/bin/env python3

'''
Utilities for MPL2 Programming Software
'''

import time
import os
import RPi.GPIO as gpio

# HEX Conversion Hash Table
hexConv = {0: 0, 1: 1, 2: 2, 3: 3,
           4: 4, 5: 5, 6: 6, 7: 7,
           8: 8, 9: 9, 'A': 10,
           'B': 11, 'C': 12, 'D':13,
           'E': 14, 'F': 15}

decConv = {0: 0, 1: 1, 2: 2, 3: 3,
           4: 4, 5: 5, 6: 6, 7: 7,
           8: 8, 9: 9, 10: 'A',
           11: 'B', 12: 'C', 13: 'D',
           14: 'E', 15: 'F'}

# SERIAL UTILITY

def read_msg(device):
    '''
    Method to collect the data being sent over
    serial to the Pi
    '''
    msg = []
    while True:

        if len(msg) > 50:
            break

        if msg == ['', '']:
            break

        rawTemp = device.read()
        msg.append(rawTemp.decode('ascii', 'ignore'))

    return msg

def send_msg(msg, device):
    '''
    Converts message into a serial-friendly
    format and sends it to the PIC
    '''
    strMsg = ''.join(msg)
    device.write(strMsg.encode('ascii'))

def make_checksum(number):
    '''
    Creates a Hexadecimal Checksum to send
    with message for verification
    '''
    checksum = 0
    for i in number[2:]:
        checksum += int(i, 16)

    if hex(checksum)[-1].isdigit():
        return hex(checksum)[-1]
    return hex(checksum)[-1].upper()

def build_sp_msg(setPoint):
    '''
    Converts calculated trip point to a message
    prefaced with an ID character and followed
    by a checksum
    '''
    spMsg = ['H', '0']
    setPoint = hex(setPoint).upper()
    for i in setPoint[2:]:
        spMsg.append(i)
    spMsg.append(make_checksum(setPoint))

    return spMsg

def filter_msg(msg):
    '''
    Removes unnecessary data from the message
    packet
    '''
    val = []
    for i in msg:
        if i not in ('\x00', ''):
            val.append(i)

    return val

def open_serial(device):
    '''
    Prevents the permissions to /dev/ttyS0 being
    blocked after closing and opening the port.
    '''
    os.system('sudo chmod a+rw /dev/ttyS0')
    device.open()

# GPIO INDICATIONS
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

# MATH UTILITY
def pull_hex_2_dec(msg):
    '''
    Combines the numbers received via serial
    and returns them as a single integer.
    '''
    concat = ''
    for i in msg[:-1]:
        if (i).isdigit():
            concat += i

    return int(concat, 16)

def conv_digits(msg):
    '''
    Checks the message for digits and converts them
    to integers for checksum use
    '''
    return [int(i) if i.isdigit() else i for i in msg]

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

if __name__ == '__main__':
    print(build_sp_msg(632))
