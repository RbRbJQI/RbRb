import serial
import time
import datetime
# import cv2
import sched

#PORT = '/dev/ttyUSB0'
PORT = 'COM5'

PRESSURE_CH1 = b'812'
PRESSURE_CH2 = b'822'
PRESSURE_CH3 = b'832'
PRESSURE_CH4 = b'842'
CURRENT_CH1 = b'811'
CURRENT_CH2 = b'821'
TEMP_CH1 = b'801'
TEMP_CH2 = b'802'

ONOFF_CH1 = b'011'
ONOFF_CH2 = b'012'


STX = b'\x02' # Start of transmission
ADDR = b'\x80' # 0x80 + device number (unused but must be present)
READ = b'\x30'
WRITE = b'\x31'
ETX = b'\x03' # End transmission
    
def getbytes(s):
    return(' '.join(hex(b)[2:].zfill(2) for b in s))

def makepacket(win, com=READ, data=None):
    payload = ADDR + win + com
    if data is not None:
        assert com == WRITE
        payload += data
    payload += ETX
    crc = payload[0]
    for b in payload[1:]:
        crc ^= b
    crc = hex(crc)[2:].upper().zfill(2).encode()
    packet = STX + payload + crc
    print('sending:', getbytes(packet))
    return packet
    
def writeread(conn, win, com=READ, data=None):
    bytes_sent = conn.write(makepacket(win, com, data))
    #print('sent %d bytes' % bytes_sent)
    response = conn.read(1024)
    #print('got response:', getbytes(response))
    #print('in ascii:', response)
    return response
    
def read_pressures():
    pressures = []
    with serial.Serial(PORT, timeout=1) as conn:
        for chan in [CURRENT_CH1, CURRENT_CH2]:
        #for chan in [PRESSURE_CH1, PRESSURE_CH2]:
            response = writeread(conn, chan)
            pressure = response[6:-3]
            pressures.append(pressure.decode())
    return pressures
	
# def read_temperatures():
    # temps = []
    # with serial.Serial(PORT, timeout=1) as conn:
        # for chan in [TEMP_CH1, TEMP_CH2]:
            # response = writeread(conn, chan)
            # temp = response[6:-3]
            # temps.append(temp.decode())
    # return temps
	
def pump_onoff(com=READ, key='off', chanlst=[ONOFF_CH1, ONOFF_CH2]):
	res = []
	with serial.Serial(PORT, timeout=1) as conn:
		for chan in chanlst:
			response = []
			if com == WRITE:
				if key == 'on':
					response = writeread(conn, chan, com, data=b'\x31')
				elif key == 'off':
					response = writeread(conn, chan, com, data=b'\x30')
			elif com == READ:
				response = writeread(conn, chan, com)
			response = response[6:-3]
			res.append(response.decode())
	return res
	
def capture_usb_cam():
	cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
	time.sleep(1.4)
	res, img = cam.read()
	cv2.imwrite("C:/Users/RbRb/Pictures/Camera Roll/" +str(datetime.datetime.now().date()) + "_" + str(datetime.datetime.now().time().hour) + "_" +
	 str(datetime.datetime.now().time().minute)+ ".png", img)
	cam.release()
	cv2.destroyAllWindows()
	del(cam)
	
def log_pressures():
    pressures = read_pressures()
    #temps = read_temperatures()
    logdata = str(datetime.datetime.now().date()) +'T'+ str(datetime.datetime.now().time())[0:5]+ ' '.join(pressures)
    # capture_usb_cam()
    #logdata = str(time.time()) + ' '+ ' '+ str(datetime.datetime.now().time()) + ' ' + ' '.join(pressures) #+ ' ' + ' '.join(temps)
    print('log currents 1/2:')
    print(logdata)
    with open('pressure_2nd_bake.log', 'a') as f:
        f.write(logdata + '\n')
        
def proc_main():
	try:
		pump_status = pump_onoff(READ)
		print('read status', pump_status)
		# if pump_status[1]=='0':
			# print('turn pump 2 on')
			# pump_onoff(WRITE, 'on', chanlst=[ONOFF_CH2])
			# print('read status', pump_onoff(READ))
		# if pump_status[0]=='0':
			# print('turn pump 1 on')
			# pump_onoff(WRITE, 'on', chanlst=[ONOFF_CH1])
			# print('read status', pump_onoff(READ))
		
		
		try:
			scheduler1 = sched.scheduler(time.time, time.sleep)
			scheduler1.enter(5, 1, log_pressures)
			scheduler1.run()
			# log_pressures()
		except Exception as e:
			print(e)
		# try:
			# print('read status', pump_onoff(READ))
			# print('turn pump 1/2 off')
			# pump_onoff(WRITE, 'off')
			# print('read status', pump_onoff(READ))
		# except Exception as e:
			# print(e)
	except Exception as e:
		print(e)

proc_main()
while True:
	print(str(datetime.datetime.now()))
	scheduler = sched.scheduler(time.time, time.sleep)
	scheduler.enter(60*10-11, 1, proc_main)
	scheduler.run()
    
# try:
	# print(pump_onoff(WRITE, 'on'))
# except Exception as e:
	# print(e)
	
# try:
	# print(pump_onoff(READ))
# except Exception as e:
	# print(e)