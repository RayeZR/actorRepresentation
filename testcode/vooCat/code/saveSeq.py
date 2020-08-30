"""
Save a video clip into a sequence of frames (the desired input of voodoo camera).
"""

import cv2
import os

inp = r'E:\I3S\actorRepresentation\testcode\PySceneDetect\05\05-Scene-014.mp4'
out_dir = r'E:\I3S\actorRepresentation\annotations\clip_05\raw_output\voocat\05_14\\'
# out_dir = r""

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

cap = cv2.VideoCapture(inp)
i = 0

ret, frame = cap.read()
while frame is not None:
    # ret, frame = cap.read()
    cv2.imwrite(out_dir + '%03d.jpg' % i, frame)
    # cv2.imshow("seq", frame)
    # cv2.waitKey(10)
    i += 1
    ret, frame = cap.read()
