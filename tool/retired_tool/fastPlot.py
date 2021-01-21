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


class MainPlot(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainPlot, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.t = [0]
        self.roi = [0]  # 100 data points
        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.t, self.roi, pen=pen)
           # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        # QtWidgets.QApplication.processEvents()
        # self.update_plot_data()
        
    def update_plot_data(self):

        # while(self.t==[]):
            # pass
        # self.roi = self.roi[1:]  # Remove the first y element.
        # self.roi.append(self.roi[-1] + 1)  # Add a new value 1 higher than the last.

        # self.t = self.t[1:]  # Remove the first 
        # self.y.append( randint(0,100))  # Add a new random value.

        self.data_line.setData(self.t, self.roi)  # Update the data.
        QtWidgets.QApplication.processEvents()
        



if __name__ == "__main__" :
    # vs = CameraStream().start()
    import time

    t,roi=[],[]
    app = QtWidgets.QApplication(sys.argv)

    w = MainPlot()
    w.show()
    # time.sleep(2)
    # Im = MainImage()
    # Im.show()
    t0 = time.time()
    # plt.ion()
    for i in range(1):
        # frame = vs.read()
        # Im.image=frame
        # plt.imshow(frame)
        t.append(time.time()-t0)
        # roi.append(np.sum(frame))
        roi.append(1)
        # plt.plot(t,roi)
        # plt.pause(0.000001)
        w.t, w.roi=t, roi
        print(i)

        # w.show()
     
        # print(i,t)
        # print(frame.dtype,frame.shape)
        # cv2.imshow('cam', np.array(frame,dtype=np.uint8))
        # if cv2.waitKey(1) == 27 :
            # break
            
    # vs.stop()
    sys.exit(app.exec_())