# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:30:16 2019

@author: CEAC Researcher
"""

### Program for controlling BK8542B DC Electronic Load for IV curve measurement of solar panel ###

import serial, time, csv, os
import pandas as pd
import itertools as it
from time import strftime
from array import array
    
global ser, ser_relay, resp_status_dict, mode_cc, mode_cv, mode_cw, mode_cr
global scale_curr, scale_volt, scale_watt, scale_resi
global r1, r2, r3, r4, r5, r6, r7, r8

global sample_id

sample_id = 29381

# Initialize PC-load serial communication and global variables

def init_load():
    """Docstring"""
    
    global ser, resp_status_dict, mode_cc, mode_cv, mode_cw, mode_cr
    global scale_curr, scale_volt, scale_watt, scale_resi

    baudrate = 9600
    port = "COM4"
    
    ser = serial.Serial(port,baudrate, timeout=1)
    
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
    scale_watt = 1000
    scale_resi = 1000    
    

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
        return (volts, current, power)
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
    """Docstring"""
    
    
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
    
    if is_remote == False:
        return False
    else:
        return True

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

def get_CP_power():
    """Docstring"""
def set_CP_power(cp_power=0):
    """Docstring"""
    
    built_packet = build_cmd(0x2E, value=int(cp_power * scale_watt))
    resp = send_recv_cmd(built_packet)
    return resp

    
    built_packet = build_cmd(0x2F)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_watt
    else:
        return None

def set_CR_resistance(cr_resistance=0):
    """Docstring"""
    
    built_packet = build_cmd(0x30, value=int(cr_resistance * scale_resi))
    resp = send_recv_cmd(built_packet)
    return resp

def get_CR_resistance():
    """Docstring"""
    
    built_packet = build_cmd(0x31)
    resp = send_recv_cmd(built_packet)
    
    if resp is not None:
        return parse_data(resp) / scale_resi
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
    
#______________________________________________________________________________
        
### Vellemen VM8090 relay card communication and control
        
def init_relay_card():
    
    global ser_relay 
    
    port = "COM5"
    baudrate = 19200
    
    ser_relay = serial.Serial(port,baudrate, timeout=1)

def close_relay():
    """Disconnect from relay card"""
    
    ser_relay.close()
    
    
def build_cmd_relay(cmd_relay, which_relay):
    """Construct command for relay card"""
    
    global r1, r2, r3, r4, r5, r6, r7, r8
    
    r1 = 0x01
    r2 = 0x02
    r3 = 0x04
    r4 = 0x08
    r5 = 0x10
    r6 = 0x20
    r7 = 0x40
    r8 = 0x80
    
    build_cmd_relay = array('B', [0x00]*7)
    
    stx = build_cmd_relay[0] 
    cmd = build_cmd_relay[1]
    msk = build_cmd_relay[2]
    param1 = build_cmd_relay[3]
    param2 = build_cmd_relay[4]
    chk = build_cmd_relay[5]
    etx = build_cmd_relay[6]
    
    
    stx = 0x04 # start byte
    cmd = cmd_relay & 0xFF # command byte
    msk = which_relay # mask byte to select relay
    chk = -(stx + cmd + msk + param1 + param2) + 1 # checksum of byte packet
    etx = 0x0F # end byte
    
    return build_cmd_relay.tobytes()

def send_cmd_relay(cmd_relay_packet):
    """Send or receive command packet from relay card"""
    
    ser_relay.reset_output_buffer()
    ser_relay.reset_input_buffer()
    
    ser_relay.write(cmd_relay_packet)
    
def switch_relay_on(which_relay):
    """Switch on one or more relays"""
    
    built_packet_relay = build_cmd_relay(0x11, which_relay)
    resp =  send_cmd_relay(built_packet_relay)
    return resp

def switch_relay_off(which_relay):
    built_packet_relay = build_cmd_relay(0x12, which_relay)
    resp =  send_cmd_relay(built_packet_relay)
    return resp
    
# Save data: current, voltage, and power

def data_file(log_file, log_file_header):
    """Docstring"""
    
    if os.path.exists(log_file) is not True:
        with open(log_file, mode='a',newline='') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(log_file_header)
            
    return log_file

def data_point(inputs: list):
    """Organizes data for export to excel"""
    
    opv = '1'
    
    timenow = strftime("%#m/%#d/%Y %#H:%M")
    volts = inputs[0]
    current = inputs[1]
    power = inputs[2]
    
    data_point = [opv, timenow, volts, current, power]
    
    return data_point
            
def write_data_tofile(data_point):
        
    global sample_id 
    
    if data_point is not None:
        sample_id += 1
        
    sample_id_lst = [sample_id]
    
    log_file = data_file()
    with open(log_file, mode='a',newline='') as the_file:
        writer = csv.writer(the_file, dialect='excel')
        writer.writerow(sample_id_lst + data_point)

# IV curve measurement
        

def open_circ():
    """Open circuit voltage measurement"""
    
    set_mode(mode_cc) # set  operation mode to CC
    time.sleep(.250)
    set_CC_current(cc_current=0) # set CC mode current to 0 amps
    time.sleep(.1)
    
    oc_vals =  get_input_values() # read open circuits levels
    oc_data_point = data_point(oc_vals) # create data point for open circuit measurement
    voc = oc_data_point[2] # open circuit voltage measurement
    print('Open circuit voltage: ', voc)
    write_data_tofile(oc_data_point) # write data to file
    
    return voc
  
def iv_curve(voc):
    """Measure intermediate current voltage points"""
    
    set_mode(mode_cv) # set operation mode to CC
    time.sleep(.250)
    volt_step = voc
    while volt_step > 0.5:
        set_CV_volts(volt_step)
        time.sleep(.1)
        curve_vals = get_input_values()
        curve_data_point = data_point(curve_vals)
        print('voltage, current, power: ', curve_data_point[2], curve_data_point[3], curve_data_point[4])
        write_data_tofile(curve_data_point)
        new_volt_step = curve_data_point[2] - 1.0
        volt_step = new_volt_step
    pass
    
def short_circ():
    """Measure short circuit current (nearest to 0 volts)"""
    
    set_mode(mode_cv)
    time.sleep(.250)
    set_CV_volts(0.1)
    time.sleep(.250)
    
    sc_vals = get_input_values()
    sc_data_point = data_point(sc_vals)
    jsc = sc_data_point[3]
    print('Short circuit current: ', jsc)
    write_data_tofile(sc_data_point)
    

def sweep():
    """Measure entire IV curve"""
    
    set_enable_load(True) # turn input ON
    time.sleep(.250)
    
    print('Begin IV curve measurement')
    
    voc = open_circ() # measure open circuit voltage
    iv_curve(voc) # measure iv curve
    short_circ() # measure short circuit current
    
    time.sleep(.250)
    set_enable_load(False) # turn input OFF

#______________________________________________________________________________
    
def process_data(in_file=str, out_file=str, opv_num=str):
    """Process data for each IV curve measurement"""
    
    out_file_header = ['opv', 'curve_id', 'time', 'hour', 'voc', 'jsc', 'mpp', 'ff']

    
    data_file(out_file, out_file_header)  
    
    df = pd.read_csv(in_file)
    
    out_file_header = ['opv', 'curve_id', 'time', 'hour', 'voc', 'jsc', 'mpp', 'ff']
    
    curve_id_count = 1
    curve = df.loc[df['curve_id'] == curve_id_count]

    while curve is not None:
        
        opv = opv_num
        time = curve['time'].iloc[0] # start time of IV curve measurement
        hour = float(time[-2] + time[-1])/60.0 + float(time[-5] + time[-4])
        voc = curve['volts'].max()
        jsc = curve['current'].max()
        mpp = curve['power'].max()
        ff = mpp / (voc * jsc)

        data_point = [opv, curve_id_count, time, hour, voc, jsc, mpp, ff]
        
        with open(out_file, mode='a',newline='') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(data_point)
        
        new_curve_id_count = curve_id_count + 1
        curve_id_count = new_curve_id_count
        
        curve = df.loc[df['curve_id'] == curve_id_count]

        pass
        
    return 
    
def match_env(opv_in_file, env_in_file, out_file):
    """Match corresponding environmental measurement to IV curve measurement"""
    
    
    df_opv = pd.read_csv(opv_in_file)
    df_env = pd.read_csv(env_in_file)
    
#    df_env['TIMESTAMP'] = pd.to_datetime(df_env['TIMESTAMP'],format='%m/%d/%y %H:%M').drop_duplicates() # 10-27-19 to 10-31-19 
    df_env['TIMESTAMP'] = pd.to_datetime(df_env['TIMESTAMP'],format='%Y-%m-%d %H:%M:%S') # 10-31-19 onwards
    df_opv['time'] = pd.to_datetime(df_opv['time'],format='%m/%d/%Y %H:%M')
    
    matched_opv_env = pd.merge(left=df_opv, left_on='time', right=df_env, right_on='TIMESTAMP')
    new_matched_opv_env = matched_opv_env.drop_duplicates().drop(['TIMESTAMP'], axis=1)
    
    new_matched_opv_env.to_csv(out_file)

#______________________________________________________________________________

def main():

    data_file('data_log_ivcurve_FIRSTRUN.csv', ['sample_id','opv', 'time' , 'volts', 'current', 'power'])
    time.sleep(.250)
    set_remote_control(True) # set remote control ON
    
    sweep()
    
    while True:
        time.sleep(900)
        sweep()

#______________________________________________________________________________
    
