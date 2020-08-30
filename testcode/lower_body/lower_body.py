"""
This script uses opencv lowerbody detector to detect the lower body of the character and mark it by a green rectangle.
"""

import cv2
import os

detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_lowerbody.xml")

inp = r"E:\I3S\actorRepresentation\code\test_data1\06-Scene-007.mp4"   # input video clip
out_dir = r"E:\I3S\actorRepresentation\code\lower_body"                # output directory

cap = cv2.VideoCapture(inp)
fps = cap.get(cv2.CAP_PROP_FPS)
[w, h] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
fourcc = cv2.VideoWriter_fourcc(*'XVID')
basename = os.path.basename(inp).split('.')[0]
writer = cv2.VideoWriter(out_dir + os.sep + basename + '_lower_body.avi', fourcc, fps, (w, h))

ret, frame = cap.read()
idx = 0
while frame is not None:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # print(gray.shape)
    rects = detector.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # cv2.imshow("res", frame)
    writer.write(frame)

    ret, frame = cap.read()
    # cv2.waitKey(5)

cap.release()
writer.release()