#! /usr/bin/env python3

'''
Set of methods for logging activity in
the MPL2 Temperature Calibration software
for error diagnostics and process feedback.
'''

import datetime

filePreface = 'Temp_Cal_'

def update_time():
    '''
    Call to update the time for time
    stamping and tracking if a new
    log file needs to be generated
    '''
    nowTime = datetime.datetime.now()
    return nowTime.strftime('%m-%d-%y')

def create_log(timeStmp):
    '''
    Generates a new log file
    '''
    file = open('Temp_Cal_Logs/' + filePreface + '%s.txt'%timeStmp, 'w')
    file.write('Temperature Calibration Log %s'%timeStmp + '\n\n')
    file.write('         Inbound Message      | Dec Val |\
                Outbound Message           | Dec Val |   Verification\n\n')
    file.close()
    return 'Temp_Cal_Logs/Temp_Cal_%s.txt'%timeStmp

def write_log(file, message):
    '''
    Writes line to log
    '''
    obj = open(file, 'a')
    obj.write(str(message) + '   ')
    obj.close()

def add_new_line(file):
    '''
    Starts new line
    '''
    obj = open(file, 'a')
    obj.write('\n')
    obj.close()
