import cv2

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 5)


       # cv2.line(img=frame, pt1=(100, 100), pt2=(500, 400), color=(255, 0, 0), thickness=5, lineType=8, shift=0)

vc.release()
cv2.destroyWindow("preview")
0001641916
0001641916
0001641916
0001641916
0001641916