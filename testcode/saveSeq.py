import cv2
import os

inp = r'E:\I3S\actorRepresentation\vooCat\lower_body\06-Scene-002.mp4'
out_dir = r'E:\I3S\actorRepresentation\vooCat\lower_body\06_02\\'

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

cap = cv2.VideoCapture(inp)
i = 0

ret, frame = cap.read()
while frame is not None:
    # ret, frame = cap.read()
    cv2.imwrite(out_dir + '%03d.jpg' % i, frame)
    cv2.imshow("seq", frame)
    cv2.waitKey(10)
    i += 1
    ret, frame = cap.read()
