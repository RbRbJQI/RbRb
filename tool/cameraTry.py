import PyCapture2
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from threading import Thread, Lock
from PyQt5 import QtWidgets, QtCore,QtGui
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

# bus = PyCapture2.BusManager()
# numCams = bus.getNumOfCameras()

# camera = PyCapture2.Camera()
# uid = bus.getCameraFromIndex(0)
# camera.connect(uid)
# print(uid)
# camInfo=camera.getCameraInfo()
# print(camInfo.serialNumber, camInfo.interfaceType, camInfo.driverType, camInfo.driverName,camInfo.vendorName)
# camera.startCapture()
# print("Start Capture")
# image = camera.retrieveBuffer()
# img_data = image.getData()
# print(img_data)
path = 'C:/Users/RbRb/Desktop/img_folder/'



class CameraStream :
    def __init__(self) :
        bus = PyCapture2.BusManager()
        self.camera = PyCapture2.Camera()
        uid = bus.getCameraFromIndex(0)
        self.camera.connect(uid)
        print(uid)
        camInfo=self.camera.getCameraInfo()
        print(camInfo.serialNumber, camInfo.interfaceType, camInfo.driverType, camInfo.driverName,camInfo.vendorName)
        self.camera.startCapture()
        image = self.camera.retrieveBuffer()#self.stream.read()
        self.frame=np.array(image.getData()).reshape((image.getRows(), image.getCols()) )
        # self.camera.stopCapture()
        self.started = False
        self.read_lock = Lock()
        self.num=0

    def start(self) :
        if self.started :
            print ("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started :
            image = self.camera.retrieveBuffer()#self.stream.read()
            frame=np.array(image.getData()).reshape((image.getRows(), image.getCols()) )
            self.read_lock.acquire()
            self.frame = frame
            self.num+=1
            self.read_lock.release()

    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        # print(self.num)
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        self.camera.stopCapture()
        self.camera.disconnect()
# plt.figure(1)
# plt.ion()
# import time
# t0 = time.time()
# for i in range(50):
    # image = camera.retrieveBuffer()
    # row_bytes = float(len(image.getData())) / float(image.getRows());
    # cv_image = np.array(image.getData()).reshape((image.getRows(), image.getCols()) );
    # plt.imshow(cv_image)
    # plt.title("t="+str(time.time()-t0)+'s')

    # plt.pause(0.001)

    # print(i)
class MainPlot(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainPlot, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.t = []
        self.roi = []  # 100 data points
        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.t, self.roi, pen=pen)
           # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0.1)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        # QtWidgets.QApplication.processEvents()
        # self.update_plot_data()
        
    def update_plot_data(self):
        global t0, vs
        frame = vs.read()
        self.t.append(time.time()-t0)
        self.roi.append(np.sum(frame))
        if len(t)>50:
            self.t.pop(0)
            self.roi.pop(0)
        self.data_line.setData(self.t, self.roi)  # Update the data.
       
        # Im.image=frame
        # plt.imshow(frame)
        
        # print(self.t, self.roi)
        # time.sleep(2)
        
        # QtWidgets.QApplication.processEvents()
        

class MainImage(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainImage, self).__init__(*args, **kwargs)

        self.graphWidget = pg.ImageView()
        self.setCentralWidget(self.graphWidget)

        # self.t = []
        self.image=[]


           # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_image_data)
        self.timer.start()
        
    def update_image_data(self):
        global vs
        self.image = vs.read()
        self.graphWidget.setImage(self.image)  # Update the data.

if __name__ == "__main__" :
    vs = CameraStream().start()
    import time

    t,roi=[],[]
    app = QtWidgets.QApplication(sys.argv)

    w = MainPlot()
    w.show()

    # Im = MainImage()
    # Im.show()
    t0 = time.time()

    for i in range(1):
        frame = vs.read()
        # Im.image=frame
        # plt.imshow(frame)
        t.append(time.time()-t0)
        roi.append(np.sum(frame))
        # roi.append(1)
        # plt.plot(t,roi)
        # plt.pause(0.000001)
        w.t, w.roi=t, roi
        # print(i)

        # w.show()
     
        # print(i,t)
        # print(frame.dtype,frame.shape)
        # cv2.imshow('cam', np.array(frame,dtype=np.uint8))
        # if cv2.waitKey(1) == 27 :
            # break
    # time.sleep(5) 

    sys.exit(app.exec_())
    vs.stop()