import numpy as np
import serial
from time import sleep
import ctypes

def read_buff(ser):
    ans = []
    while True:
        ans.append(ser.readline().decode())
        if ans[-1]=='': break
        sleep(0.1)
    if len(ans)>1: print(ans[0:-2])
    return ans[0:-2]
    
def cmd(ser, s):
    ser.write(s)
    sleep(1)
    return read_buff(ser)

user_input = input("Turn on or off the BoosTA?(Y/N): ")
if user_input=='Y': max_curr = input("Tell me the max curr in mA (e.g. 1500): ")
ser = serial.Serial()
ser.port = 'COM8'
ser.baudrate = 19200
ser.timeout = 0.5
ser.open()

if ser.isOpen() and user_input=='Y':
    ans = cmd(ser, b'remote on\r')
    sleep(1)
    ans = cmd(ser, b'lcurr 500\r')
    sleep(5)
    ans = cmd(ser, b'laon on\r')
    I_c = np.arange(700, int(max_curr), 250)
    if I_c[-1]<int(max_curr): I_c = np.append( I_c, int(max_curr) )
    for II in I_c:
        t = 0
        exit_while = False
        while True:
            sleep(3)
            t += 3
            ans = read_buff(ser)
            for an in ans:
                if 'stabilized' in an:
                    exit_while = True
            if t>60 or exit_while: break
        cmd_str = 'lcurr ' + str(II) + '\r'
        print('Input: '+cmd_str)
        ans = cmd(ser, cmd_str.encode())
    ctypes.windll.user32.MessageBoxW(0, "The TA curr has reached "+max_curr, "BoosTA Serial", 1)
elif ser.isOpen and user_input=='N':
    ans = cmd(ser,b'laoff\r')
    ctypes.windll.user32.MessageBoxW(0, "The TA is off", "BoosTA Serial", 1)
    
ser.close()
