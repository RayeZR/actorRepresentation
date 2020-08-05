import cv2
import os

inp = r'E:\I3S\actorRepresentation\data\ffmpeg\03\03_10.mp4'
out_dir = r'E:\I3S\actorRepresentation\vooCat\test\03_10\\'

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

cap = cv2.VideoCapture(inp)
i = 0

while(cap.isOpened()):
    ret, frame = cap.read()
    if frame is not None:
        cv2.imwrite(out_dir + '%03d.jpg' % i, frame)
        cv2.imshow("seq", frame)
        cv2.waitKey(10)
        i += 1
