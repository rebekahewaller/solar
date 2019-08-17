# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:30:16 2019

@author: CEAC Researcher
"""

### Program for controlling BK8542B DC Electronic Load for IV curve measurement of solar panel ###

import serial, time
#import bk8500b #getting Name Error whenever attempting to use function from library

# Input data: serial communication, number of samples, PV data
    
# Serial communication configuration (PC-load) and start

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
        bk8500b.printCmd(resp)
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
    curr_in = resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)
    return curr_in/10000.00

def readInputLevels(serial):
    print("Read input voltage, current, power and relative state")
    cmd = [0] * 26 # byte 3 to 6 = voltage (1 mV), byte 7 to 10 = current (0.1 mA)
    cmd[2] = 0x5F # byte 11 to 14 = power (1 mW)
    resp = command(cmd, serial)
    volt_in = resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)
    curr_in = resp[7] + (resp[8] << 8) + (resp[9] << 16) + (resp[10] << 24)
    pow_in = resp[11] + (resp[12] << 8) + (resp[13] << 16) + (resp[14] << 24)
    return volt_in/1000.00, curr_in/10000.00, pow_in/1000.00
        
def opencircuit(serial):
    setMode(0,serial) # Set operation mode to CC
    readMode(serial) # Read operation mode
    setCCCurrent(0,serial) # Set CC mode current to 0 amps
    readCCCurrent(serial)
    readInputLevels(serial)
    
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
    command(cmd, serial)
    
def curve(opv_voc,serial):
    steps = 0
    setMode(1,serial)
    readMode(serial)
        
        

# Short circuit proof

# Set local control mode ON

def setLocalMode(serial):
    cmd = [0] * 26
    cmd[2] = 0x20
    cmd[3] = 0
    command(cmd, serial)
    print("Goodbye")
    ser.close()
    
# Save data: current, voltage, and power