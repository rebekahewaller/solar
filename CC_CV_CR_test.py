# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:30:16 2019

@author: CEAC Researcher
"""

### Program for controlling BK8542B DC Electronic Load for IV curve measurement of solar panel ###

import serial, time, csv, os

d_log = None

#import bk8500b #getting Name Error whenever attempting to use function from library

# Input data: serial communication, number of samples, PV data
    
# Serial communication configuration (PC-load) and start

def init_load():
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = "COM3"
    ser.timeout = 1
    ser.open()
    ser.flush

def csum(command):  
    checksum = 0
    for i in range(25):     
        checksum = checksum + command[i]                    
    return (0xFF & checksum)

def printCmd(buff):
    x = " "        
    for y in range(len(buff)):
        x+=" "
        x+=hex(buff[y]).replace('0x','')   
    print(x)      

def command(command, serial):                          
    command[0] = 0xAA
    command[25] = csum(command)
    serial.write(command)                        
    resp = serial.read(26)
    if resp[2] == 0x12:
        if resp[3] == 0x80:
            print('Success')
            return
        elif resp[3] == 0x90:
            raise Exception('Checksum Error')
        elif resp[3] == 0xA0:
            raise Exception('Parameter Incorrect')
        elif resp[3] == 0xB0:
            raise Exception('Unrecognized Command')
        elif resp[3] == 0xC0:
            raise Exception('Invalid Command')
            
        print("Command Sent:\t\t",end=' ')
        printCmd(command)
            
        print("Reponse Received:\t",end=' ')     
        printCmd(resp)
    else:
        return resp

# Setting protection functions: current, voltage, and power

# Set remote control ON

def remoteMode(state, serial):
    print('Remote Mode')
    cmd = [0] * 26
    cmd[2] = 0x20
    if bool(state):
        cmd[3] = 1
    else:
        cmd[3] = 0
    command(cmd, serial)

def inputOn(state, serial):
    print('Input On', state)
    cmd = [0] * 26
    cmd[2] = 0x21
    if bool(state):
        cmd[3] = 1
    else:
        cmd[3] = 0
    command(cmd, serial)
    
def inputOff(serial):
    print("Turning Input OFF")
    cmd = [0] * 26
    cmd[2] = 0x21                       
    command(cmd, serial)
    
# Open circuit proof

def setMode(mode, serial):
    print("Set CC/CV/CW/CR operation mode of electronic load.")
    cmd = [0] * 26
    cmd[2] = 0x28
    cmd[3] = mode # CC = 0, CV = 1, CW = 2, CR = 3
    command(cmd, serial)

def readMode(serial):
    print("Read the operation mode.")
    cmd = [0] * 26
    cmd[2] = 0x29
    command(cmd, serial)
    
def setCCCurrent(curr, serial):
    print("Set CC mode current value (amps):", curr)
    val = int(curr * 10000)
    cmd = [0] * 26
    cmd[2] = 0x2A
    cmd[3] = val & 0xFF
    cmd[4] = (val >> 8) & 0xFF
    cmd[5] = (val >> 16) & 0xFF
    cmd[6] = (val >> 24) & 0xFF
    command(cmd, serial)
    
def readCCCurrent(serial):
    print("Read CC mode current value")
    cmd = [0] * 26
    cmd[2] = 0x2B
    resp = command(cmd, serial)
    curr_in_CC = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 10000.00
    return curr_in_CC

def readInputLevels(serial):
    print("Read input voltage, current, power and relative state")
    cmd = [0] * 26 # byte 3 to 6 = voltage (1 mV), byte 7 to 10 = current (0.1 mA)
    cmd[2] = 0x5F # byte 11 to 14 = power (1 mW)
    resp = command(cmd, serial)
    volt_in = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 1000.00
    curr_in = (resp[7] + (resp[8] << 8) + (resp[9] << 16) + (resp[10] << 24)) / 10000.00
    power_in = (resp[11] + (resp[12] << 8) + (resp[13] << 16) + (resp[14] << 24)) / 1000.00
    op_state = hex(resp[15])
    demand_state = hex((resp[16] + resp[17] << 8))
    return (volt_in, curr_in, power_in, op_state, demand_state)
        
def opencircuit(serial):
    setMode(0,serial) # Set operation mode to CC
    readMode(serial) # Read operation mode
    setCCCurrent(0,serial) # Set CC mode current to 0 amps
    time.sleep(1)
    readCCCurrent(serial)
    reading = readInputLevels(serial)
    voc = reading[0]
    return voc
    
# Intermediate steps: sampling between open circuit voltage and short circuit current

def setCVVoltage(volt, serial): # need to add in hex conversion
    print("Set CV mode voltage value (volts):", volt)
    val = int(volt * 1000)
    cmd = [0] * 26
    cmd[2] = 0x2C
    cmd[3] = val & 0xFF
    cmd[4] = (val >> 8) & 0xFF
    cmd[5] = (val >> 16) & 0xFF
    cmd[6] = (val >> 24) & 0xFF
    command(cmd, serial)
    
def readCVVoltage(serial):
    print("Read CV mode voltage value")
    cmd = [0] * 26
    cmd[2] = 0x2D
    resp = command(cmd, serial)
    volt_in_CV = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 1000.00
    return volt_in_CV
    
def curve(voc, log_file, serial):
    step_count = 0
    setMode(1,serial)
    readMode(serial)
    time.sleep(1)
    setCVVoltage(voc,serial)
    readCVVoltage(serial)
    time.sleep(1)
    for step_count in range(100):
        reading = readInputLevels(serial)
        volt_step = reading[0]
        new_volt_step = volt_step - 0.1
        if new_volt_step > 0:
            setCVVoltage(new_volt_step,serial)
            readCVVoltage(serial)
            curve_pt = readInputLevels(serial)
            print(curve_pt)
            write_data(log_file, [time.time(),  curve_pt[0], curve_pt[1], curve_pt[2]])
            step_count += 1
            time.sleep(1)
        else:
            return None
        
# Short circuit proof
        
def shortcircuit(serial):
    setMode(1,serial) # Set operation mode to CV
    readMode(serial) # Read operation mode
    time.sleep(1)
    setCVVoltage(0.1,serial) # Set CV mode voltage to 0.1 volts (nearest value to 0 volts)
    time.sleep(1)
    readCVVoltage(serial)
    reading = readInputLevels(serial)
    jsc = reading[1]
    return jsc

# Set local control mode ON

def setLocalMode(serial):
    cmd = [0] * 26
    cmd[2] = 0x20
    cmd[3] = 0
    command(cmd, serial)
    print("Goodbye")
    ser.close()
    
# Save data: current, voltage, and power

def data_file(header_list, log_file_postfix=''):
    
    log_file = 'data_log_' + log_file_postfix + '.csv'
    log_file_header = header_list
    
    if os.path.exists(log_file) is not True:
        with open(log_file, mode='a') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(header_list)
            
def write_data(log_file, data_list):
        
    with open(log_file, mode='a') as the_file:
        writer = csv.writer(the_file, dialect='excel')
        writer.writerow(data_list)


def main():
    
    print('Setup DC load and logging')
    init_load()
    data_file(['Time' , 'volts', 'current', 'power'], log_file_postfix='LOAD')
    
    print('Begin IV curve measurement')
    
    opencircuit()
    curve()
    shortcircuit()
    
    
    
    