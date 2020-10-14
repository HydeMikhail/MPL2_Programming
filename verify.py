#! /usr/bin/env python3

'''
Copy of the Programming Master Program. Instead of sending a Trip Point
to the PIC, this program sends a character to instruct the PIC to output
it's current stored trip point.

For details on the fixture and electrical connections please see the
programming_master.py file.
'''

import time
import os
import serial
import RPi.GPIO as gpio
import gen_util

##################
### GPIO SETUP ###
##################

### Global Pin Values ###

vdd = 18
vpp = 23
tx = 14
rx = 15
passLed = 17
idleLed = 27
statusLed = 22
startBut = 5
endBut = 6
tempPin = 4

### Board Mode Setting ###

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

### Initialization ###

gpio.setup(vdd, gpio.OUT)
gpio.setup(vpp, gpio.OUT)
gpio.setup(passLed, gpio.OUT)
gpio.setup(idleLed, gpio.OUT)
gpio.setup(statusLed, gpio.OUT)

gpio.output(vdd, gpio.HIGH)
gpio.output(vpp, gpio.HIGH)
gpio.output(passLed, gpio.HIGH)
gpio.output(idleLed, gpio.HIGH)
gpio.output(statusLed, gpio.HIGH)

gpio.setup(startBut, gpio.IN)
gpio.setup(endBut, gpio.IN)

gpio.setup(tempPin, gpio.IN)

### Serial Comm Permissions ###

os.system('sudo chmod a+rw /dev/ttyS0')

### Set up serial port (initialized to closed) ###

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1, stopbits=2)
ser.close()

### Startup Hold ###

time.sleep(3)

### System Ready Indication ###

gpio.output(passLed, gpio.LOW)
gpio.output(statusLed, gpio.LOW)

### Float Tx ###

gen_util.idle_uart(tx)

#################
### Main Loop ###
#################

while True:

    # Exit Program if Button is Pressed
    if gpio.input(endBut):
        gen_util.exit_seq(passLed, idleLed, statusLed)
        break

    # When Program button is pressed
    if gpio.input(startBut):

        # Initialize Serial Protocol
        gen_util.start_seq(vdd, vpp, idleLed, statusLed)
        gen_util.active_uart()
        time.sleep(0.48)
        gen_util.open_serial(ser)

        try:
            # Collect Message
            msg = gen_util.read_msg(ser, 6, 200)
            ser.close()
            # Verify Temperature Reading Message
            if msg == [] or msg[0] != 'G':
                gen_util.error_ind(idleLed)
            else:
                # Verify Checksum from Incoming Message to Continue
                if gen_util.verify_checksum(msg):
                    # Calculate/Build Set Point Message
                    try:
                        gen_util.open_serial(ser)
                        gen_util.send_msg('X', ser)
                        input('Press Enter to Continue: ')
                        time.sleep(0.005)
                        gen_util.idle_uart(tx)
                    except ValueError:
                        gen_util.error_ind(idleLed)
                else:
                    gen_util.error_ind(idleLed)

        except serial.SerialException:
            gen_util.error_ind(idleLed)

        # Reset system to prepare for next calibration
        gen_util.end_seq(vdd, vpp, idleLed, statusLed)
        ser.close()

    # Sets Program loop rate. Keeps CPU from full-throttling
    time.sleep(0.00005)

gpio.cleanup()
