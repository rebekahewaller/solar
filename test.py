#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 12:23:40 2019

@author: bekah

BARD OPV project
BK Precision 8542B DC Electronic Load program for IV curve measurement
"""

# Make sure that DC Load protocol is FRAME, SYS->PROTOCOL, to control with 26 byte commands

import serial
import time

portNUM = input("Which COMM Port? ") # Enter comm port that DC Load is connected to on PC
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM' + portNUM
ser.timout = 1
ser.open()
ser.flush

### SET UP ###
 
cmd=[0xAA,0,0x20,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0xCB]  # Set the control mode to remote
                                                                    # This gives a preview as to the format.
ser.write(cmd)
confirm = ser.read(26)                                              # NO ERROR response
print(confirm)                                                      

cmd=[0xAA,0,0x5D,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x07]  # Set function mode to fixed
ser.write(cmd)
print(ser.read(26))
print("\n")

### FUNCTIONS ###

def csum(command):                                                  # Automatically calculate the checkSum
    sum = 0
    for i in range ((len(command) - 1)):
        sum += command[i]
    return (0xFF & sum)

def Printer(read):                                                  # Make 26 byte command format more readable
    x = " "
    for y in range(len(read)):
        x+=" "
        x+=hex(read[y]).replace('0x','')
    print(x)
                                                                    
ser.write(cmd)                                                      # Write command to serial port
print(ser.read(26))                                                 # Read the response. The response 0x12/0x08 is an error free confirmation
                                                                    # MUST read response every time, otherwise responses will queue up

def Command(com):                                                   # Send commands and receive replies
    com[0] = 0xAA                                                   # Automatically sets start bit
    com[25] = csum(com)                                             # Automatically places checksum
    print("Command Sent:\t\t",end=' ')                              
    Printer(com)                                                    # Prints command in readable format
    ser.write(com)                                                  # Writes the command
    print("Response Received:\t",end=' ')
    resp = ser.read(26)
    if(resp == confirm):                                            # If we receive the no error string, print "No Error" 
        print("\tNo Error")
    else:                                                           # Else print the string
        Printer(resp)
        print("\n")
        
### LIST FUNCTION FOR IV CURVE MEASUREMENT ###
        
print("\n")
print("Creating current list for IV curve measurement")
print("\n")

print("Reading function mode")                                      
cmd = [0]*26                                                        # Reading list function mode
cmd[2] = 0x5E
Command(cmd)

print("Reading List 1")                                             
cmd = [0]*26                                                        
cmd[2] = 0x4D                                                       # Selecting List 1
cmd[3] = 1
Command(cmd)

print("Setting List operation mode to Constant Current")            
cmd = [0]*26                                                        
cmd[2] = 0x3B                                                       # Reading List operation mode
Command(cmd)

print("Setting List to 21 steps")
cmd = [0]*26                                                        
cmd[2] = 0x3E                                                       # Setting List 1 Step Counts to 21 Steps
cmd[3] = 0x15
Command(cmd)

print("Reading List step count")    
cmd = [0]*26                                                        
cmd[2] = 0x3F                                                       # Reading List Step Count
Command(cmd)

time.sleep(1)
print("Compiling List")
cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 1                                                          # List Step 1
cmd[4] = 0

cmd[5] = 0x01                                                       # 6th, 7th, 8th, 9th bytes are current amplitude values                                                                    
cmd[6] = 0x00                                                       # .0001 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       # 10th and 11th bytes are time values. 0x01 represents 0.1ms
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 2                                                          # List Step 2
cmd[4] = 0

cmd[5] = 0xF4                                                                                                                           
cmd[6] = 0x01                                                       # .05 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)



cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 3                                                          # List Step 3
cmd[4] = 0

cmd[5] = 0xE8                                                                                                                           
cmd[6] = 0x03                                                       # .1 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 4                                                          # List Step 4
cmd[4] = 0

cmd[5] = 0x14                                                                                                                           
cmd[6] = 0x05                                                       # .13 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 5                                                          # List Step 5
cmd[4] = 0

cmd[5] = 0x46                                                                                                                           
cmd[6] = 0x05                                                       # .135 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 6                                                          # List Step 6
cmd[4] = 0

cmd[5] = 0x78                                                                                                                           
cmd[6] = 0x05                                                       # .14 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 7                                                          # List Step 7
cmd[4] = 0

cmd[5] = 0xAA                                                                                                                           
cmd[6] = 0x05                                                       # .145 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 8                                                          # List Step 8
cmd[4] = 0

cmd[5] = 0xDC                                                                                                                           
cmd[6] = 0x05                                                       # .15 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 9                                                          # List Step 9
cmd[4] = 0

cmd[5] = 0x0E                                                                                                                           
cmd[6] = 0x06                                                       # .155 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 10                                                         # List Step 10
cmd[4] = 0

cmd[5] = 0x40                                                                                                                           
cmd[6] = 0x06                                                       # .16 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 11                                                         # List Step 11
cmd[4] = 0

cmd[5] = 0x72                                                                                                                           
cmd[6] = 0x06                                                       # .165 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 12                                                         # List Step 12
cmd[4] = 0

cmd[5] = 0xA4                                                                                                                           
cmd[6] = 0x06                                                       # .17 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 13                                                         # List Step 13
cmd[4] = 0

cmd[5] = 0xD6                                                                                                                           
cmd[6] = 0x06                                                       # .175 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 14                                                         # List Step 14
cmd[4] = 0

cmd[5] = 0x08                                                                                                                           
cmd[6] = 0x07                                                       # .18 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 15                                                         # List Step 15
cmd[4] = 0

cmd[5] = 0x3A                                                                                                                           
cmd[6] = 0x07                                                       # .185 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 16                                                         # List Step 16
cmd[4] = 0

cmd[5] = 0x6C                                                                                                                           
cmd[6] = 0x07                                                       # .19 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 17                                                         # List Step 17
cmd[4] = 0

cmd[5] = 0xD0                                                                                                                           
cmd[6] = 0x07                                                       # .20 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 18                                                         # List Step 18
cmd[4] = 0

cmd[5] = 0x34                                                                                                                           
cmd[6] = 0x08                                                       # .21 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


cmd = [0]*26                                                        
cmd[2] = 0x40                                                       # Setting List Step Value
cmd[3] = 19                                                         # List Step 19
cmd[4] = 0

cmd[5] = 0x98                                                                                                                           
cmd[6] = 0x08                                                       # .22 Amperes
cmd[7] = 0x00
cmd[8] = 0x00

cmd[9] = 0x88                                                       
cmd[10] = 0x13                                                      # 0.5 second
Command(cmd)


time.sleep(1)
print("\n")
print("Saving List")
cmd = [0]*26
cmd[2] = 0x4C                                                       # Saving List 
cmd[3] = 1                                                          # To Slot 1
Command(cmd)
time.sleep(1)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 1                                                          # Step 1
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 2                                                          # Step 2
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 3                                                         # Step 3
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 4                                                          # Step 4
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 5                                                          # Step 5
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 6                                                          # Step 6
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 7                                                          # Step 7
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 8                                                          # Step 8
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 9                                                          # Step 9
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 10                                                         # Step 10
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 11                                                         # Step 11
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 12                                                         # Step 12
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 13                                                         # Step 13
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 14                                                         # Step 14
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 15                                                         # Step 15
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 16                                                         # Step 16
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 17                                                         # Step 17
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 18                                                         # Step 18
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 19                                                         # Step 19
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 20                                                         # Step 20
Command(cmd)


print("Reading List")
cmd = [0]*26                                                        
cmd[2] = 0x41                                                       # Reading Step Value
cmd[3] = 21                                                         # Step 21
Command(cmd)


print("Setting Trigger Mode to Bus")
cmd = [0]*26
cmd[2] = 0x58                                                       # Set Trigger Mode to Bus, allows for triggering remotely
cmd[3] = 2                                                          # Bus (software) trigger.                                  
Command(cmd)                                                        # NOTE FOR CR3000 VOLTAGE TRIGGER, SELECT 1

print("Turning Input ON")
cmd = [0]*26
cmd[2] = 0x21                                                      
cmd[3] = 0x01                                                                                            
Command(cmd)

print("Entering List Mode")
cmd = [0]*26
cmd[2] = 0x5D                                                       # Selecting List Function Mode                                                   
cmd[3] = 3                                                                                            
Command(cmd)

print("Sending Trigger Signal")
cmd = [0]*26
cmd[2] = 0x5A                                                      # Send Trigger Signal                                                                                          
Command(cmd)

time.sleep(1800)                                                   # 30 minute delay till next reading