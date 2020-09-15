#! /usr/bin/env python3

'''
Set of methods for logging activity in
the MPL2 Temperature Calibration software
for error diagnostics and process feedback.
'''

import datetime

def update_time():
    '''
    Call to update the time for time
    stamping and tracking if a new
    log file needs to be generated
    '''
    nowTime = datetime.datetime.now()
    return nowTime.strftime('%m-%d-%y')

def create_log(timeStamp):
    '''
    Generates a new log file
    '''
    file = open('Temp_Cal_Logs/Temp_Cal_%s.txt'%timeStamp, 'w')
    file.write('Temperature Calibration Log %s'%timeStamp)
    file.close()

def write_log(inMsg, outMsg):
    '''
    Writes line to log
    '''
    pass

if __name__ == '__main__':
    time = update_time()
    create_log(time)
