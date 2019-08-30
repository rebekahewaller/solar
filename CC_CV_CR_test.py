# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:30:16 2019

@author: CEAC Researcher
"""

### Program for controlling BK8542B DC Electronic Load for IV curve measurement of solar panel ###

import argparse, serial, time, sched, csv, os # matplotlib, pandas
from time import strftime
from serial import Serial
from array import array

# Input data: serial communication, number of samples, PV data
    
# Serial communication configuration (PC-load) and start

ser = serial.Serial()
ser.baudrate = 9600
ser.port = "COM3"
ser.timeout = 1
ser.open()
ser.flush
return ser

# _____________________________________________________________________________

def get_args():
    """Get command line arguments"""
    
    parser = argparse.ArgumentParser(
            description='Argparse Python script',
            formatter_class=argparse.ArgumentDefaultHelpFormatter)
    
    parser.add_argument('-p',
                        '--port',
                        help='Com Port',
                        metavar='str',
                        type=str,
                        default='COM3')
    
    parser.add_argument('-b',
                        '--baudrate',
                        help='Baud rate',
                        metavar='int',
                        type=int,
                        default=9600)
    
    parser.add_argument('-t',
                        '--time_to_sleep',
                        help='Time seconds to sleep b/w commands',
                        metavar='float',
                        type=float,
                        default=0.250)
    
    parser.add_argument('-c',
                        '--mode_cc',
                        help='Constant current mode',
                        metavar='int',
                        type=int,
                        default=0)
    
    parser.add_argument('-v',
                    '--mode_cc',
                    help='Constant voltage mode',
                    metavar='int',
                    type=int,
                    default=1)
    
    parser.add_argument('-w',
                        '--mode_cv',
                        help='Constant voltage mode',
                        metavar='int',
                        type=int,
                        default=2)
    
    parser.add_argument('-r',
                        '--mode_cr',
                        help='Constant resistance mode',
                        metavar='int',
                        type=int,
                        default=3)


def init_load(port, baudrate, timeout):
    """Docstring"""
    
    baudrate = baudrate
    port = port
    
    ser = Serial(port,baudrate, timeout=1)
    
    resp_status_dict = {
            0x90: "ERROR: Invalid checksum",
            0xA0: "ERROR: Invalid value",
            0xB0: "ERROR: Unable to execute",
            0xC0: "ERROR: invalid command",
            0x80: True,
        }

    mode_cc = 0 # constant current mode
    mode_cv = 1 # constant voltage mode
    mode_cw = 2 # constant power mode
    mode_cr = 3 # constant resistance mode
    
    scale_volt = 1000
    scale_curr = 10000
    scale_watt = 10000    

def close():
    """Docstring"""
    ser.close()

def parse_data(resp):
    """Docstring"""
    
    data = resp[4] | (resp[5] << 8) | (resp[6] << 16) | (resp[7] << 24)
    print(data)
    return data

def check_resp(resp):
    """Docstring"""    
    
    if len(resp) == 26:

        # Confirm start byte
        if resp[0] == 0xAA:
            resp_type = resp[2]

            if resp_type == 0x12:  # Status type
                return resp_status_dict[resp[3]]
            else:
                return True

        else:
            print('Start byte mismatch')
            return None

    else:
        print('Packet length mismatch')
        return None                            

def build_cmd(cmd, value=None):
    """Docstring"""
    
    build_cmd = array('B', [0x00]*26)

    build_cmd[0] = 0xAA  # Packet start
    build_cmd[1] = 0x00  # Unsupported address location
    build_cmd[2] = cmd & 0xFF  # Command value

    if value is not None:
        build_cmd[3] = value & 0xFF  # value 1st byte little endian
        build_cmd[4] = (value >> 8) & 0xFF  # value 2nd byte little endian
        build_cmd[5] = (value >> 16) & 0xFF  # value 3rd byte little endian
        build_cmd[6] = (value >> 24) & 0xFF  # value 4th byte little endian

    checksum = 0
    for item in build_cmd:
        checksum += item
    checksum %= 256

    build_cmd[25] = checksum & 0xFF

    return build_cmd.tobytes()

def send_recv_cmd(cmd_packet):
    """Docstring"""
    
    # House cleaning, flush serial input and output bufferss
    ser.reset_output_buffer()
    ser.reset_input_buffer()

    # Send and receive
    ser.write(cmd_packet)
    time.sleep(0.250)  # Provide time for response
    resp_array = array('B', ser.read(26))  # get resp and put in array

    check = check_resp(resp_array)

    if check is True:
        return resp_array
    else:
        print('Response check failed')
        print(check)
        return None

def get_device_info():
    """Docstring"""
    
    built_packet = build_cmd(0x6A)
    resp = send_recv_cmd(built_packet)

    if resp is not None:
        model = chr(resp[3]) + chr(resp[4]) + chr(resp[5]) + chr(resp[6])
        version = str(resp[9]) + '.' + str(resp[8])
        serial = chr(resp[10]) + chr(resp[11]) + chr(resp[12]) + chr(resp[13]) + chr(resp[14]) + chr(resp[16]) + chr(resp[17]) + chr(resp[18]) + chr(resp[19])
        return (model, version, serial)
    else:
        return None

def get_input_values():
    """Docstring"""
    
    built_packet = build_cmd(0x5F)
    resp = send_recv_cmd(built_packet)

    if resp is not None:
        volts = (resp[3] | (resp[4] << 8) | (resp[5] << 16) | (resp[6] << 24)) / scale_volt
        current = (resp[7] | (resp[8] << 8) | (resp[9] << 16) | (resp[10] << 24)) / scale_curr
        power = (resp[11] | (resp[12] << 8) | (resp[13] << 16) | (resp[14] << 24)) / scale_watt
        op_state = hex(resp[15])
        demand_state = hex(resp[16] | (resp[17] << 8))
        return (volts, current, power, op_state, demand_state)
    else:
        return None

def set_function(function):
    """Docstring"""
    
    built_packet = build_cmd(0x5D, value=function)
    resp = send_recv_cmd(built_packet)
    return resp

def get_function():
    built_packet = build_cmd(0x5E)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return resp[3]
    else:
        return None

def set_remote_sense(is_remote=False):
    """Docstring"""
    
    built_packet = build_cmd(0x56, value=int(is_remote))
    resp = send_recv_cmd(built_packet)
    return resp

def get_remote_sense():
    "Docstring"""
    
    
    built_packet = build_cmd(0x57)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp)
    else:
        return None

def set_remote_control(is_remote=False):
    """Docstring"""
    
    built_packet = build_cmd(0x20, value=int(is_remote))
    resp = send_recv_cmd(built_packet)
    return resp

def set_local_control(is_local=True):
    """Docstring"""
    
    built_packet = build_cmd(0x55, value=int(is_local))
    resp = send_recv_cmd(built_packet)
    return resp

def set_mode(mode):
    """Docstring"""
    
    built_packet = build_cmd(0x28, value=mode)
    resp = send_recv_cmd(built_packet)
    return resp

def get_mode():
    """Docstring"""
    
    built_packet = build_cmd(0x29)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp)
    else:
        return None

def set_enable_load(is_enabled=False):
    """Docstring"""
    
    built_packet = build_cmd(0x21, value=int(is_enabled))
    resp = send_recv_cmd(built_packet)
    return resp

def set_max_volts(max_volts=0):
    """Docstring"""
    
    
    built_packet = build_cmd(0x22, value=int(max_volts))
    resp = send_recv_cmd(built_packet)
    return resp

def get_max_volts():
    """Docstring"""
    
    
    built_packet = build_cmd(0x23)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_volt
    else:
        return None

def set_max_current( max_current=0):
    """Docstring"""
    
    
    built_packet = build_cmd(0x24, value=int(max_current * scale_curr))
    resp = send_recv_cmd(built_packet)
    return resp

def get_max_current():
    """Docstring"""
    
    
    built_packet = build_cmd(0x25)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_curr
    else:
        return None

def set_max_power( max_power=0):
    """Docstring"""
    
    
    built_packet = build_cmd(0x24, value=int(max_power * scale_watt))
    resp = send_recv_cmd(built_packet)
    return resp

def get_max_power():
    """Docstring"""
    
    
    built_packet = build_cmd(0x27)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_volt
    else:
        return None

def set_CV_volts(cv_volts=0):
    """Docstring"""
    
    
    built_packet = build_cmd(0x2C, value=int(cv_volts * scale_volt))
    resp = send_recv_cmd(built_packet)
    return resp

def get_CV_volts():
    """Docstring"""
    
    
    built_packet = build_cmd(0x2D)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_volt
    else:
        return None

def set_CC_current(cc_current=0):
    """Docstring"""
    
    
    built_packet = build_cmd(0x2A, value=int(cc_current * scale_curr))
    resp = send_recv_cmd(built_packet)
    return resp

def get_CC_current():
    """Docstring"""
    
    built_packet = build_cmd(0x2B)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_curr
    else:
        return None

def set_CP_power(cp_power=0):
    """Docstring"""
    
    built_packet = build_cmd(0x2E, value=int(cp_power * scale_watt))
    resp = send_recv_cmd(built_packet)
    return resp

def get_CP_power():
    """Docstring"""
    
    built_packet = build_cmd(0x2F)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_watt
    else:
        return None

def set_CR_resistance(cr_resistance=0):
    """Docstring"""
    
    built_packet = build_cmd(0x30, value=int(cr_resistance * SCALE_RESIST))
    resp = send_recv_cmd(built_packet)
    return resp

def get_CR_resistance():
    """Docstring"""
    
    built_packet = build_cmd(0x31)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / SCALE_RESIST
    else:
        return None

def set_bat_volts_min(min_volts=3):
    """Docstring"""
    
    built_packet = build_cmd(0x4E, value=int(min_volts * scale_volt))
    resp = send_recv_cmd(built_packet)
    return resp

def get_bat_volts_min():
    """Docstring"""
    
    built_packet = build_cmd(0x4F)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_volt
    else:
        return None
    
# Save data: current, voltage, and power

def make_data_file(header_list, log_file_postfix=''):
    """Docstring"""
    
    header_list = ['opv', 'sample_id', 'time' , 'volts', 'current', 'power']

    log_file = 'data_log_' + log_file_postfix + '.csv'
    log_file_header = header_list
    
    if os.path.exists(log_file) is not True:
        with open(log_file, mode='a',newline='') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(header_list)
            
def make_data_list(opv, sample_id, timenow, volt, curr, watt):
    """Organizes data for export to excel"""
    
    data_list = [opv, sample_id, timenow, volt, curr, watt]
    
            
def write_data_tofile(log_file, data_list):
        
    with open(log_file, mode='a',newline='') as the_file:
        writer = csv.writer(the_file, dialect='excel')
        writer.writerow(data_list)
    
def open_circ():
    """Open circuit voltage measurement"""

    set_mode(mode_cc) # set  operation mode to CC
    time.sleep(.250)
    set_CC_current(cc_current=0) # set CC mode current to 0 amps
    time.sleep(.250)
    get_input_values() # read open circuits levels
    
    


def opencircuit(opv_sample, log_file, serial):
    print("Open circuit voltage measurement")
    setMode(0,serial) # Set operation mode to CC
    time.sleep(.5)
    setCCCurrent(0,serial) # Set CC mode current to 0 amps
    time.sleep(.5)
    oc = readInputLevels(serial) # Read open circuit levels
    write_data(log_file, [opv_sample, strftime("%a, %d %b %Y %H:%M:%S"),  oc[0], oc[1], oc[2]]) # write data to .csv file
    voc = oc[0] # open circuit voltage
    print(voc)
    return voc   
    
    
#______________________________________________________________________________

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
    
# VOn Mode turns on load only if certain voltage is reached
    
def setVonMode(mode,serial):
    print("Set Von mode to:", mode)
    cmd = [0] * 26
    cmd[2] = 0x0E
    if mode == 'living':
        cmd[3] = 0x00 #Von LIVING mode
    elif mode == 'latch':
        cmd[3] = 0x01 #Von LATCH 
    else:
        print("Von mode not specified")
    command(cmd, serial)

def readVonMode(serial):
    print("Read Von mode")
    cmd = [0] * 26
    cmd[2] = 0x0F
    resp = command(cmd, serial)
    return resp

def setVonPoint(von_volt, serial):
    print("Set Von point (volts):", von_volt)
    val = int(von_volt * 1000)
    cmd = [0] * 26
    cmd[2] = 0x10
    cmd[3] = val & 0x00FF
    cmd[4] = (val >> 8) & 0xFF
    cmd[5] = (val >> 16) & 0xFF
    cmd[6] = (val >> 24) & 0xFF
    command(cmd, serial)

def readVonPoint(serial):
    print("Read Von point")
    cmd = [0] * 26
    cmd[2] = 0x11
    resp = command(cmd, serial)
    von_volt = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 1000.00
    return von_volt

# Open circuit proof

def setMode(mode, serial):
#    print("Set CC/CV/CW/CR operation mode of electronic load.")
    cmd = [0] * 26
    cmd[2] = 0x28
    cmd[3] = mode # CC = 0, CV = 1, CW = 2, CR = 3
    command(cmd, serial)

def readMode(serial):
#    print("Read the operation mode.")
    cmd = [0] * 26
    cmd[2] = 0x29
    command(cmd, serial)
    
def setCCCurrent(curr, serial):
#    print("Set CC mode current value (amps):", curr)
    val = int(curr * 10000)
    cmd = [0] * 26
    cmd[2] = 0x2A
    cmd[3] = val & 0xFF
    cmd[4] = (val >> 8) & 0xFF
    cmd[5] = (val >> 16) & 0xFF
    cmd[6] = (val >> 24) & 0xFF
    command(cmd, serial)
    
def readCCCurrent(serial):
#    print("Read CC mode current value")
    cmd = [0] * 26
    cmd[2] = 0x2B
    resp = command(cmd, serial)
    curr_in_CC = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 10000.00
    return curr_in_CC

def readInputLevels(serial):
#    print("Read input voltage, current, power and relative state")
    cmd = [0] * 26 # byte 3 to 6 = voltage (1 mV), byte 7 to 10 = current (0.1 mA)
    cmd[2] = 0x5F # byte 11 to 14 = power (1 mW)
    resp = command(cmd, serial)
    volt_in = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 1000.00
    curr_in = (resp[7] + (resp[8] << 8) + (resp[9] << 16) + (resp[10] << 24)) / 10000.00
    power_in = (resp[11] + (resp[12] << 8) + (resp[13] << 16) + (resp[14] << 24)) / 1000.00
#    op_state = hex(resp[15])
#    demand_state = hex((resp[16] + resp[17] << 8))
    return (volt_in, curr_in, power_in)
        
def opencircuit(opv_sample, log_file, serial):
    print("Open circuit voltage measurement")
    setMode(0,serial) # Set operation mode to CC
    time.sleep(.5)
    setCCCurrent(0,serial) # Set CC mode current to 0 amps
    time.sleep(.5)
    oc = readInputLevels(serial) # Read open circuit levels
    write_data(log_file, [opv_sample, strftime("%a, %d %b %Y %H:%M:%S"),  oc[0], oc[1], oc[2]]) # write data to .csv file
    voc = oc[0] # open circuit voltage
    print(voc)
    return voc
    
# Intermediate steps: sampling between open circuit voltage and short circuit current

def setCVVoltage(volt, serial):
#    print("Set CV mode voltage value (volts):", volt)
    val = int(volt * 1000)
    cmd = [0] * 26
    cmd[2] = 0x2C
    cmd[3] = val & 0xFF
    cmd[4] = (val >> 8) & 0xFF
    cmd[5] = (val >> 16) & 0xFF
    cmd[6] = (val >> 24) & 0xFF
    command(cmd, serial)
    
def readCVVoltage(serial):
#    print("Read CV mode voltage value")
    cmd = [0] * 26
    cmd[2] = 0x2D
    resp = command(cmd, serial)
    volt_in_CV = (resp[3] + (resp[4] << 8) + (resp[5] << 16) + (resp[6] << 24)) / 1000.00
    return volt_in_CV
    
def curve(voc, opv_sample, log_file, serial):
    print("Measure intermediate current-voltage points")
    setMode(1,serial)
    time.sleep(1)
    volt_step = voc
    while volt_step > 0.5:
        setCVVoltage(volt_step,serial)
        time.sleep(0.1)
        curve_pt = readInputLevels(serial)
        print(curve_pt)
        write_data(log_file, [opv_sample, strftime("%a, %d %b %Y %H:%M:%S"), curve_pt[0], curve_pt[1], curve_pt[2]])
        new_volt_step = curve_pt[0] - 0.5
        volt_step = new_volt_step
        time.sleep(0.1)
    time.sleep(1)
    setCVVoltage(1,serial)            
    
# Short circuit proof
        
def shortcircuit(opv_sample, log_file, serial):
    print("Measure short circuit current (nearest to 0 volts)")
    setMode(1,serial) # Set operation mode to CV
    time.sleep(.5)
    setCVVoltage(0.1,serial) # Set CV mode voltage to 0.1 volts (nearest value to 0 volts)
    time.sleep(1)
    sc = readInputLevels(serial)
    write_data(log_file, [opv_sample, strftime("%a, %d %b %Y %H:%M:%S"),  sc[0], sc[1], sc[2]])
    jsc = sc[1]
    print(jsc)
    return jsc

# Set local control mode ON

def setLocalMode(serial):
    cmd = [0] * 26
    cmd[2] = 0x20
    cmd[3] = 0
    command(cmd, serial)
    print("Goodbye")
    serial.close()
    
# Save data: current, voltage, and power

def data_file(header_list, log_file_postfix=''):
    
    log_file = 'data_log_' + log_file_postfix + '.csv'
    log_file_header = header_list
#    header_list = ['OPV', 'Time' , 'volts', 'current', 'power']
    
    if os.path.exists(log_file) is not True:
        with open(log_file, mode='a',newline='') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(header_list)
            
def write_data(log_file, data_list):
        
    with open(log_file, mode='a',newline='') as the_file:
        writer = csv.writer(the_file, dialect='excel')
        writer.writerow(data_list)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
# Main testing function for IV curve measurement

def sweep(opv_sample, serial):
        
    inputOn(1,serial)
        
    time.sleep(0.5)
    
    print('Begin IV curve measurement')

    log_file = 'data_log_LOAD.csv'
    
    voc = opencircuit(opv_sample, log_file, serial)
    
    time.sleep(0.5)
    
    curve(voc, opv_sample, log_file, serial)
    
    time.sleep(0.5)
    
    shortcircuit(opv_sample, log_file, serial)
    
    time.sleep(0.5)
    
    inputOff(serial)
        
    
def main():
    
#    serial = init_load()

    time.sleep(1)
    
    remoteMode(1,serial) # magic numbers... what do they mean???
    
    time.sleep(1)
    
    data_file(['opv_sample', 'time' , 'volts', 'current', 'power'], log_file_postfix='LOAD')
    
    time.sleep(1)

    # determine which OPV is connected
    opv_sample = '1'
    
    sweep(opv_sample,serial)
    
    s = sched.scheduler(time.time, time.sleep)
    
    s.enter(15, 1, sweep, (opv_sample, serial)) # need different function to only execute after 30 seconds has elapsed since function was complete
    
    s.run()
    
    
# conditional statement for init_load function
# improve datalogging with sweep ids and identifying MPP, Voc, Jsc for each sweep
# measure time for executing each function
# create class for and generalize write_data function
    
# pylint 
# change all "serial" vars to "srl"
# pure functions are functions that can be tested
    
if __name__ == '__main__':
    main()
    
