import threading
import time
import cv2

cap = cv2.VideoCapture('rtsp://admin:cev123456@192.168.1.108/cam/realmonitor?channel=1&subtype=1')
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
counter = 0

while True:
   ret, frame = cap.read()
   if ret:
       cv2.imwrite('2.jpg', frame)
       #counter = counter + 1




