import serial
import time

PORT = '/dev/ttyUSB0'
#PORT = 'COM6'

PRESSURE_CH1 = b'812'
PRESSURE_CH2 = b'822'
PRESSURE_CH3 = b'832'
PRESSURE_CH4 = b'842'

STATUS = b'205'


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
    #print('sending:', getbytes(packet))
    return packet
    
def writeread(conn, win, com=READ, data=None):
    bytes_sent = conn.write(makepacket(win, com, data))
    print('sent %d bytes' % bytes_sent)
    response = conn.read(1024)
    #print('got response:', getbytes(response))
    #print('in ascii:', response)
    return response
    
def read_pressures():
    pressures = []
    with serial.Serial(PORT, timeout=1) as conn:
        for chan in [PRESSURE_CH1, PRESSURE_CH2]:
            response = writeread(conn, chan)
            pressure = response[6:-3]
            pressures.append(pressure.decode())
    return pressures

def log_pressures():
    pressures = read_pressures()
    logdata = str(time.time()) + ' ' + ' '.join(pressures)
    print(logdata)
    with open('pressure_2nd_bake.log', 'a') as f:
        f.write(logdata + '\n')
        

conn = serial.Serial(PORT, timeout=1)
		
while True:
    try:
        packet = makepacket(STATUS)
        print( conn.write( packet ) )
        print( conn.read(1024) )
		
    except Exception as e:
        print(e)
    time.sleep(5)