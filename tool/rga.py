import getpass
import telnetlib
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime
import h5py

HOST = "169.254.153.121"
user = "mks113-a061002"#input("Enter your remote account: ")
password = "mksrga1"#getpass.getpass()

tn = telnetlib.Telnet(HOST, timeout=1)
tn.open(HOST, port=10014, timeout=1)

def cmd(ccmd):
	tn.write(ccmd.encode('ascii')+ b"\n")
	print(tn.read_until(b"\r\r"))
	
def Analog(name, Points_per_peak, Accu, Det_ind=0):
	st = "1 "
	end = "50 "
	Points_per_peak = str(Points_per_peak) + " "
	Accu = str(Accu) + " "
	Det_ind = str(Det_ind) + " "
	ccmd = "AddAnalog " + name + " " + st + end + Points_per_peak + Accu + "0 0 "+ Det_ind + "\r"
	cmd(ccmd)
	cmd("ScanAdd "+name)
	cmd("ScanStart 1")
	#read all the trash
	while 1:
		try:
		#read zeromass
			zeroMass,zeroPressure=extract(str(tn.read_until(b"\r\r")),"ZeroReading ")
			print(zeroMass, zeroPressure)
			break
		except:
			continue
	total_num=(int(end)-int(st)+1)*int(Points_per_peak)
	print(total_num)
	data=np.zeros( (total_num,2) )
	i = 0
	while i<total_num:
		try:
			data[i,0:2]=extract(str(tn.read_until(b"\r\r")),"MassReading ")[0:2]
			data[i,1]=data[i,1]-zeroPressure
			i+=1
		except:
			print('exception at ',i)
			continue
	cmd("ScanStop")
	return data
	
def extract(str, expect):# read content between expect and \r from str
	try:
		data=str.split(expect)[1]
		mass,pressure = data.split(" ")[0], data.split(" ")[-1]
		pressure = pressure[:-9]
		return float(mass), float(pressure)
	except Exception as e:
		print(str)
		# print(e)

print(tn.read_until(b"\r\r"))
cmd("Control ms 5.1\r")
cmd("FilamentControl On")
# interested = np.array([2,8,18,28,32,40,44])
# clr = ['b','r','g','y','k','c','m']
interested = np.array([2,18,28,44])
clr = ['b','g','y','m']
Points_per_peak = 8
interested = Points_per_peak * interested - int(Points_per_peak/2)
#trace = []
peak_jump = []
dt = []
dtime = []
while(1):
	hf = h5py.File("C:/Users/RbRb/Desktop/RGA_log_3rd_bake.h5",'a')
	dtime = list(hf['time'].value)
	dt = [datetime.fromtimestamp(dti) for dti in dtime]
	dt = [str(dti)[:-10] for dti in dt]
	dt.append(str(datetime.now())[:-10])
	dtime.append(time.time())
	del hf['/time']
	hf.create_dataset('/time', data=dtime)
	data = Analog("a1", Points_per_peak, Accu=6, Det_ind=2)
	data = np.array(data)
	#analog
	plt.figure(1)
	plt.plot(data[:,0], data[:,1])
	plt.yscale('log')
	plt.savefig("C:/Users/RbRb/Desktop/analog_3rd.png")
	plt.clf()
	#trace.append(data)
	#peak jump
	trnum = len(interested)
	plt.figure(2)
	lgd = []
	for j in range(trnum):
		lgd.append(data[interested[j],0])
		tr = list(hf['/'+str(lgd[j])].value)
		tr.append(data[interested[j],1])
		# tr = np.array(trace)[:,interested[j],1]
		# lgd.append(trace[-1][interested[j],0])
		plt.plot(dt, tr, clr[j])
		del hf['/'+str(lgd[j])]
		hf.create_dataset('/'+str(lgd[j]), data=tr)
	plt.xticks(range(0,len(dt),max(int(len(dt)/4),1)), dt[0:len(dt):max(int(len(dt)/4),1)], rotation = 10)
	plt.yscale('log')
	plt.legend(tuple(lgd))
	plt.savefig("C:/Users/RbRb/Desktop/Time_trace.png")
	plt.clf()
	hf.close()
	time.sleep(15*60)
# cmd("FilamentControl Off")
cmd("Release")
tn.close()
# python desktop/rga.py