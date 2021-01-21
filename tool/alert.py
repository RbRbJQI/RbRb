from serial import *
from threading import *
from time import *
import re
import numpy as np

last_received = ''
warn_temp = 19

def receiving(ser,run_event):
    global last_received
    buffer = ''
    tt = 0
    while run_event.is_set():
        # last_received = ser.readline()
        buffer = ser.read(ser.inWaiting()).decode()
        if '\n' in buffer:
            last_received = buffer.split('\n')[:-1]
            # print(last_received)
            text = ""
            for line in last_received[-11:]:
                matchObj = re.match( r'Channel_(.*) C =(.*?)\r', line, re.M|re.I)
                channel_name = np.int64(matchObj.group(1).split('\n'))
                channel_temp = np.int64(matchObj.group(2).split('\n'))
                # print(channel_temp)
                if np.max(channel_temp)>=warn_temp:
                    for i in range(len(channel_temp)):
                        if channel_temp[i]>=warn_temp:
                            text += 'Warning: Temp too high on Channel %d C=%d\n'%(channel_name[i], channel_temp[i])
            if len(text):
                print(text,'\n')
                send_sms(text)
        sleep(25)
        if tt%2==0:
            print(buffer)
        tt += 1

def send_sms(msg):
    from twilio.rest import Client

    # Your Account SID from twilio.com/console
    account_sid = "AC6699b98ddc811da832437cd2fc1b7cf8"
    # Your Auth Token from twilio.com/console
    auth_token  = "1ec02a3d526d245aaf52676f3c37206f"

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to="+13014549473", 
        from_="+12057514423",
        body=msg)
    message = client.messages.create(
        to="+12408986039", 
        from_="+12057514423",
        body=msg)
        

    print(message.sid)

if __name__ ==  '__main__':
    run_event = Event()
    run_event.set()
    ser = Serial(
        port='COM13',
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
        timeout=0.1,
        xonxoff=0,
        rtscts=0,
        interCharTimeout=1
    )
    t1 = Thread(target=receiving, args=(ser,run_event))
    t1.start() 
    try:
        while 1:
            sleep(.1)
    except KeyboardInterrupt:
        run_event.clear()
        t1.join()