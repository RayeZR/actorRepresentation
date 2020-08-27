"""
This script is used to crop the top and bottom fixed areas in all the frames in a video clip.
Edges are detected using Canny edge detection and the most salient horizontal row (by taking the maximum sum of the
pixels in a row) are marked as the edge of the top/bottom. Then the other edge is computed symmetrically by subtracting
this row index from the height of the frame.
The crop height (row index) can also be assigned manually using --crop_h.
The desired area without the top and bottom zones are saved as clip_xx_crop.avi
To avoid some opening shots with no content, the frame to be detected is sampled from the 20s by default, which can be
modified using --sec.

Example command: python preprocess.py --inp_file E:\I3S\actorRepresentation\dataset\clip_06.mp4
"""

import argparse
import os
import cv2
import numpy as np


class Preprocess:
    def __init__(self, inp_file, out_dir, sec=20):
        self.inp_file = inp_file
        self.cap = cv2.VideoCapture(inp_file)
        self.out_dir = out_dir
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.sec = sec
        self.w, self.h = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def onmouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x, y)
            # return (x, y)
            # self.x = x
            # self.y = y

    def detect(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(img, 100, 200)
        # cv2.imshow("edge", edges)
        accum_edge_val = np.sum(edges, axis=1)
        idx_1 = np.argmax(accum_edge_val)
        idx_2 = self.h - idx_1
        self.upper, self.lower = min(idx_1, idx_2), max(idx_1, idx_2)
        print(self.upper, self.lower)


    def read(self):
        ret, frame = self.cap.read()
        cnt = 0
        while frame is not None:
            cnt += 1
            # print(cnt)
            if cnt == self.sec * round(self.fps):
                # cv2.namedWindow("vid")
                # cv2.imshow("vid", frame)
                # cv2.setMouseCallback("vid", self.onmouse)
                # cv2.setMouseCallback("vid", self.onmouse)
                # cv2.waitKey(20000)
                self.detect(frame)
                self.cap.release()
                break
            ret, frame = self.cap.read()

    def set_crop_height(self, crop_h):
        self.upper = crop_h
        self.lower = self.h - crop_h

    def crop_and_save(self):
        self.cap = cv2.VideoCapture(self.inp_file)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer= cv2.VideoWriter(self.out_dir, self.fourcc, self.fps, (self.w, (self.lower - self.upper - 1)))
        ret, frame = self.cap.read()
        while frame is not None:
            cropped = frame[(self.upper+1):self.lower, :, :]
            writer.write(cropped)
            ret, frame = self.cap.read()
        self.cap.release()
        writer.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_file", required=True, help="the original video clip to be cropped")
    parser.add_argument("--sec", default=20, help="sample frame timestamp (seconds)")
    parser.add_argument("--crop_h", default=-1, help="manually assigned crop height")
    parser.add_argument("--out_dir", default="", help="output file name")

    args = vars(parser.parse_args())
    inp_file = args["inp_file"]
    sec = args["sec"]
    crop_h = args["crop_h"]
    out_dir = args["out_dir"]
    if out_dir == "":
        out_dir = inp_file.replace(".mp4", "_crop.avi")
    process = Preprocess(inp_file, out_dir, sec)
    if crop_h == -1:
        process.read()
    else:
        process.set_crop_height(crop_h)
    process.crop_and_save()