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

class UnlockDevice(object):

    KEY_POS = (620, 920)

    HELP_MENU = (
        '============================================',
        '    UnlockDeviceTest',
        '============================================',
        'options: -t n [-k n,n] [-s on/off]',
        '  -t n: set times to test',
        '  -k n,n: set unlock key position',
        '     default set: -k %s,%s' % (KEY_POS[0], KEY_POS[1]),
        '  -s on/off: current state: power on or off.',
        '',
        'Note: power device to locked state before test.',
    )

    def __init__(self):
        self._unlock_times = 0  # test times.
        self._state = 1 # power on and locked.
        self._key_pos = self.KEY_POS # key position (620, 920) ,(500, 600)

    def send_power(self):
        cmd = 'adb shell input keyevent 26'
        subprocess.call(cmd, shell=True)

    def send_unlock(self):
        cmd = 'adb shell input tap %s %s' % (self._key_pos[0], self._key_pos[1])
        subprocess.call(cmd, shell=True)

    def get_input_opts(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'ht:k:s:')
        except getopt.GetoptError as e:
            print(str(e))
            opts = None
        else:
            for name, value in opts:
                if name == '-h':
                    for usage in self.HELP_MENU:
                        print(usage)
                    sys.exit()
                if name == '-t':
                    self._unlock_times = int(value)
                if name == '-k':
                    pos = value.split(',')
                    self._key_pos = tuple(pos)
                if name == '-s':
                    if value == 'on':
                        self._state = 1
                    else:
                        self._state = 0
        return opts

    def run_unlock_test(self):
        for index in range(self._unlock_times):
            print('Test: %d/%d' % (index + 1, self._unlock_times))
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
        # power on after test.
        self.send_power()
        print('all of %d times test done!\n' % self._unlock_times)


if __name__ == '__main__':
    unlock = UnlockDevice()
    # get input args.
    opts = unlock.get_input_opts()
    if not opts:
        sys.exit()
    # run test.
    if unlock._unlock_times:
        # relock device for test.
        if unlock._state:
             # power down
            unlock.send_power()
            time.sleep(2)
        unlock.send_power()
        time.sleep(4)
        # start to test unlock
        unlock.run_unlock_test()
