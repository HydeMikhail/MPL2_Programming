#! /usr/bin/env python3

'''
Main Program to coordinate temperature calibration with MPL2
driver board.

PHYSICAL GPIO:
37 - 3.3 V   (VDD) ::: Provides power to PIC
6 - GND      (GND) ::: Provides ground to PIC
18 - GPIO     (VPP) ::: Used to signal start of programming procedure
8 - Tx       (CLK) ::: Transmit Pin
10 - Rx      (DAT) ::: Receive Pin

11 - GPIO (OUT)    ::: Pass LED (GREEN)
12 - GPIO (OUT)    ::: Idle LED (RED)
16 - GPIO (OUT)    ::: Status LED (WHITE)

13 - GPIO (IN)     ::: Trigger Calibration Button
15 - GPIO (IN)     ::: Close Application Button

7 - GPIO (IN)     ::: Temperature Data

The Pi is integrated with a fixture including 5 pins to interface
with the MPL2 driver board, 2 indicator LEDs, and two buttons to
trigger programming and exit the application.

When the board is interfaced with the fixture/pi and the trigger button
is pressed the Pi provides power to the PIC and pulls VPP low, indicating
to the PIC that a temperature calibration procedure should be started. The
PIC then takes 32 temperature readings, averages those msgues, and sends an
ASCII msgue to the Pi via UART. This program receives that msgue and passes
it through a model, which was determined experimentally, that calcuates the
expected msgue at 80 C based on the room temperature reading. The Pi will then
send that msgue back to the PIC, which will store that msgue in it's memory.

To verify this process, the PIC will then send back a checksum to confirm that
the msgue it received is correct. At this point, the green LED will turn on to
show the operator that the process was successful. If, at any point, there is an
issue, the red idle LED will flash to indicate the issue.
'''

import time
import os
from os import path
import serial
import RPi.GPIO as gpio
import gen_util
import log_util
import temp_util

##################
### GPIO SETUP ###
##################

### Global Pin Values ###

vdd = 26
vpp = 24
tx = 14
rx = 15
passLed = 17
idleLed = 18
statusLed = 23
startBut = 27
endBut = 22
tempPin = 4

### Logging Setup ###

timeStamp = log_util.update_time()
file = 'Temp_Cal_Logs/' + log_util.filePreface + timeStamp + '.txt'
if not path.exists(file):
    log_util.create_log(timeStamp)

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
        log_util.add_new_line(file)
        log_util.write_log(file, 'Program Exited\n')
        break

    # When Program button is pressed
    if gpio.input(startBut):

        # Initialize Serial Protocol
        gen_util.start_seq(vdd, vpp, idleLed, statusLed)
        gen_util.active_uart()
        time.sleep(0.53)
        gen_util.open_serial(ser)

        try:
            # Collect Message
            msg = gen_util.read_msg(ser, 6, 50)
            ser.close()
            if len(msg) > 0:
                log_util.write_log(file, str(msg)
                                   + '    '
                                   + str(gen_util.hex_2_dec(msg, 1))
                                   + '    ')
            # Verify Temperature Reading Message
            if msg == [] or msg[0] != 'G':
                log_util.write_log(file, 'Message Incomplete\n')
                gen_util.error_ind(idleLed)
            else:
                # Verify Checksum from Incoming Message to Continue
                if gen_util.verify_checksum(msg):
                    # Calculate/Build Set Point Message
                    temp = temp_util.read_temp()
                    setPoint = gen_util.calc_set_point(gen_util.hex_2_dec(msg, 1), temp)
                    spMsg = gen_util.build_sp_msg(setPoint)
                    if len(spMsg) == 8:
                        log_util.write_log(file, str(spMsg)
                                           + '    '
                                           + str(gen_util.hex_2_dec(spMsg, 3))
                                           + '      ')
                    else:
                        log_util.write_log(file, 'Outbound Message Error'
                                           + '                  ')
                    # Send Message to PIC
                    gen_util.open_serial(ser)
                    gen_util.send_msg(spMsg, ser)
                    time.sleep(0.005)
                    gen_util.idle_uart(tx)
                    # Read Verification Message
                    reply = gen_util.read_msg(ser, 1, 50)
                    if reply == ['Y']:
                        log_util.write_log(file, 'Verified')
                        gen_util.pass_ind(idleLed, statusLed, passLed)
                    else:
                        log_util.write_log(file, 'Unverified')
                        gen_util.error_ind(idleLed)
                else:
                    log_util.write_log(file, 'Checksum incorrect. Bad Message')
                    gen_util.error_ind(idleLed)

        except serial.SerialException:
            log_util.write_log(file, 'Serial Exception. Problem with communication.')
            gen_util.error_ind(idleLed)

        # Reset system to prepare for next calibration
        gen_util.end_seq(vdd, vpp, idleLed, statusLed)
        ser.close()
        log_util.add_new_line(file)

    # Sets Program loop rate. Keeps CPU from full-throttling
    time.sleep(0.00005)

gpio.cleanup()
