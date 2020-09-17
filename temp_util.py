#! /usr/bin/env python3

'''
Tools for handling the temperature sensor
for the MPL2 Programming Fixture
'''

import os
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

baseDir = '/sys/bus/w1/devices/'
deviceFolder = glob.glob(baseDir + '28*')[0]
deviceFile = deviceFolder + '/w1_slave'

def read_temp_raw():
    '''
    Reads raw temperature output from
    sensor.
    '''
    tempFile = open(deviceFile, 'r')
    lines = tempFile.readlines()
    tempFile.close()
    return lines

def read_temp():
    '''
    Converts raw temperature reading
    into a usable float value.
    '''
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        lines = read_temp_raw()
    equalsPos = lines[1].find('t=')
    if equalsPos != -1:
        tempString = lines[1][equalsPos+2:]
        return float(tempString) / 1000.0

if __name__ == '__main__':
    while True:
        print(read_temp())
        time.sleep(1)
