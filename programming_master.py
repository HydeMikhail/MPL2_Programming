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

os.system('sudo chmod a+rw /dev/ttyS0')

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
ser.close()

time.sleep(3)

gpio.output(11, gpio.LOW)
gpio.output(16, gpio.LOW)

while True:

    if gpio.input(13):

        util.start_seq(37, 7, 12, 16)
        time.sleep(0.25)
        util.open_serial(ser)

        try:
            rt = ser.readline()
        except serial.SerialException:
            print('Serial Exception. Problem with communication.')
            print(rt)
            util.error_ind(12)

        try:
            sp = util.calc_set_point(int(rt.decode('ascii', 'ignore')))
            print(sp)
            util.pass_ind(12, 16, 11)
        except ValueError:
            print('Value Error. Value Received was not an integer.')
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
