#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on: 2018-12-28

@author: Zbyng Zeng
"""

import sys
import getopt
import subprocess
import time

class UnlockDeviceTest(object):

    USAGE = (
        '============================================',
        '    UnlockDeviceTest',
        '============================================',
        'options: -t n [-k n,n]',
        '  -t n: set times to test',
        '  -k n,n: set unlock key position',
        '     default set: 500,600',
        '',
        'Note: power device to locked state before test.',
    )

    def __init__(self):
        self._cnt = 50  # test times.
        self._state = 1 # power on and locked.
        self._key_pos = (500, 600) # key position (620, 920)

    def send_power(self):
        cmd = 'adb shell input keyevent 26'
        subprocess.call(cmd, shell=True)

    def send_unlock(self):
        cmd = 'adb shell input tap %s %s' % (self._key_pos[0], self._key_pos[1])
        subprocess.call(cmd, shell=True)

    def get_test_args(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'ht:k:')
        except getopt.GetoptError as e:
            print(str(e))
        else:
            for name, value in opts:
                if name == '-h':
                    for usage in self.USAGE:
                        print(usage)
                    sys.exit()
                if name == '-t':
                    self._cnt = int(value)
                if name == '-k':
                    pos = value.split(',')
                    self._key_pos = tuple(pos)

    def run_test(self):
        for index in range(self._cnt):
            print('Test: %d/%d' % (index + 1, self._cnt))
            # no send power on while the first time and power on.
            if index != 0:
                print('power up')
                self.send_power() # power up
                time.sleep(4)
            # unlock device.
            print('unlock')
            self.send_unlock() # unlock
            time.sleep(4)
            # power off to lock device.
            #print('power off')
            self.send_power() # power down
            time.sleep(2)


if __name__ == '__main__':
    unlock = UnlockDeviceTest()
    unlock.get_test_args()
    unlock.run_test()
