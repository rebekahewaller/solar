#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2019-08-28
Purpose: Rock the Casbah
"""

import argparse
import os
import sys
import serial, time, sched, csv, os


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-b',
                        '--baudrate',
                        help='Baud rate',
                        metavar='int',
                        type=int,
                        default=9600)

    parser.add_argument('-p',
                        '--port',
                        help='Port',
                        metavar='str',
                        type=str,
                        default='COM3')

    parser.add_argument('-T',
                        '--timeout',
                        help='Timeout',
                        metavar='int',
                        type=int,
                        default=1)

    parser.add_argument('-t',
                        '--time_to_sleep',
                        help='Time to sleep b/w commands',
                        metavar='float',
                        type=float,
                        default=1.)

    return parser.parse_args()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    baud_rate = args.baudrate
    port = args.port
    time_to_sleep = args.time_to_sleep
    timeout = args.timeout

    s = sched.scheduler(time.time, time.sleep)

    print('baud rate = "{}"'.format(baud_rate))
    print('port = "{}"'.format(port))

    srl = init_load(baud_rate, port, timeout)

    time.sleep(time_to_sleep)

    remote_mode(


# --------------------------------------------------
def init_load(baud_rate, port, timeout):
    """Docstring"""

    ser = serial.Serial()
    ser.baudrate = baud_rate
    ser.port = port
    ser.timeout = timeout

    try:
        ser.open()
        ser.flush
    except:
        pass
    finally:
        return ser

    # SerialException: could not open port 'COM3': PermissionError(13, 'Access is denied.', None, 5)


# --------------------------------------------------
if __name__ == '__main__':
    main()
