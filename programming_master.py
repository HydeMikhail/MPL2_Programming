#! /usr/bin/env python3

'''
Main Program to coordinate temperature calibration with MPL2
driver board.

PHYSICAL GPIO:
37 - 3.3 V   (VDD) ::: Provides power to PIC
6 - GND      (GND) ::: Provides ground to PIC
7 - GPIO     (VPP) ::: Used to signal start of programming procedure
8 - Tx       (CLK) ::: Transmit Pin
10 - Rx      (DAT) ::: Receive Pin

11 - GPIO (OUT)    ::: Pass LED (GREEN)
12 - GPIO (OUT)    ::: Idle LED (RED)
16 - GPIO (OUT)    ::: Status LED (WHITE)

13 - GPIO (IN)     ::: Trigger Calibration Button
15 - GPIO (IN)     ::: Close Application Button

The Pi is integrated with a fixture including 5 pins to interface
with the MPL2 driver board, 2 indicator LEDs, and two buttons to
trigger programming and exit the application.

When the board is interfaced with the fixture/pi and the trigger button
is pressed the Pi provides power to the PIC and pulls VPP low, indicating
to the PIC that a temperature calibration procedure should be started. The
PIC then takes 32 temperature readings, averages those values, and sends an
ASCII value to the Pi via UART. This program receives that value and passes
it through a model, which was determined experimentally, that calcuates the
expected value at 80 C based on the room temperature reading. The Pi will then
send that value back to the PIC, which will store that value in it's memory.

To verify this process, the PIC will then send back a checksum to confirm that
the value it received is correct. At this point, the green LED will turn on to
show the operator that the process was successful. If, at any point, there is an
issue, the red idle LED will flash to indicate the issue.
'''

import time
import os
import serial
import RPi.GPIO as gpio
import util

# HEX Conversion Hash Table
hexConv = {'a': 10, 'b': 11, 'c': 12, 'd':13, 'e': 14, 'f': 15}

# GPIO SETUP
gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)

gpio.setup(7, gpio.OUT)
gpio.setup(11, gpio.OUT)
gpio.setup(12, gpio.OUT)
gpio.setup(16, gpio.OUT)
gpio.setup(37, gpio.OUT)

gpio.output(7, gpio.HIGH)
gpio.output(11, gpio.HIGH)
gpio.output(12, gpio.HIGH)
gpio.output(16, gpio.HIGH)
gpio.output(37, gpio.LOW)

gpio.setup(13, gpio.IN)
gpio.setup(15, gpio.IN)

# Serial Comm Permissions
os.system('sudo chmod a+rw /dev/ttyS0')

# Set up serial port (initialized to closed)
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
ser.close()

# Startup Time
time.sleep(3)

# System Ready Indication
gpio.output(11, gpio.LOW)
gpio.output(16, gpio.LOW)

while True:

    # When Program button is pressed
    if gpio.input(13):

        msg = []
        val = []

        util.start_seq(37, 7, 12, 16)
        time.sleep(0.53)
        util.open_serial(ser)

        try:
            while True:

                if len(msg) > 50:
                    break

                if msg == ['', '']:
                    break

                rt = ser.read()
                msg.append(rt.decode('ascii', 'ignore'))

            for i in msg:
                if i not in ('\x00', ''):
                    val.append(i)

            val = [int(i) if i.isdigit() else i.lower() for i in val]

            if val == [] or val[0] != 'g':
                util.error_ind(12)
            else:
                if sum(val[1:5]) == hexConv[val[5]]:
                    util.pass_ind(12, 16, 11)
                else:
                    util.error_ind(12)

        except serial.SerialException:
            print('Serial Exception. Problem with communication.')
            util.error_ind(12)

        util.end_seq(37, 7, 12, 16)
        ser.close()
        # Send Trip point to PIC
        # Wait for response
        # Verify response
        # Activate PASS LED

    if gpio.input(15):
        break

    time.sleep(0.001)

gpio.cleanup()
