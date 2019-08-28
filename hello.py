#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2019-08-28
Purpose: Rock the Casbah
"""

import argparse
import os
import sys


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('name',
                        metavar='str',
                        help='A name')

    parser.add_argument('-n',
                        '--num',
                        metavar='int',
                        default=1,
                        type=int,
                        help='Number of times to greet')

    return parser.parse_args()


# --------------------------------------------------
def greet(name, excited = False):
    """Say hello"""

    return 'Hello, {}{}'.format(name, '!' if excited else '.')


# --------------------------------------------------
def test_greet():
    """Test Say hello"""

    assert greet('Bekah') == 'Hello, Bekah.'
    assert greet('Ken') == 'Hello, Ken.'
    assert greet('Bekah', excited=True) == 'Hello, Bekah!'
    assert greet('Ken', excited=True) == 'Hello, Ken!'


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()

    for _ in range(args.num):
        print(greet(args.name))


# --------------------------------------------------
if __name__ == '__main__':
    main()
