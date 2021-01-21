import numpy as np
from PIL import ImageGrab
import cv2 as cv
import pytesseract
from gtts import gTTS
import playsound
import os
import win32gui
import time

def read_scr(bbox):
	img = ImageGrab.grab(bbox=bbox)
	img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
	cv.imwrite(r'C:\Users\RbRb\Desktop\scrst.jpg', img)

	pytesseract.pytesseract.tesseract_cmd = r'C:\Users\RbRb\AppData\Local\Tesseract-OCR\tesseract.exe'
	code = pytesseract.image_to_string(img)
	print(code)

	tts = gTTS(code, lang='en')
	filename = 'C:/Users/RbRb/Desktop/tmp/temp.mp3'
	tts.save(filename)

	playsound.playsound(filename)
	os.remove(filename)

while 1:
	flags, hcursor, (x,y) = win32gui.GetCursorInfo()
	print(x,y)
	try:
		bbox = (x,y, x+120, y+60)
		read_scr(bbox)
	except Exception as e:
		print(e)
		time.sleep(1)