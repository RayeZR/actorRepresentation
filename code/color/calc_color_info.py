"""
This is the revised script to save the peak and average color information of the frames.

Example command: python calc_color_info.py --inp_dir E:\I3S\actorRepresentation\dataset --out_dir \
E:\I3S\actorRepresentation\annotations
"""

import argparse
import os
import cv2
import numpy as np
from math import floor, ceil
import json
import time

'''
res = {"0": {"RGBL-all-ave": [1, 3, 3, 2], "RGBL-all-peak": [5, 6, 6, 4],
             "RGBL-UL-ave":  [3, 4, 1, 2], "RGBL-UL-peak":  [6, 8, 3, 5],
             "RGBL-UC-ave":  ..., "RGBL-UC-peak": ...,
             ...
             "RGBL-C-ave":   ..., "RGBL-C-peak": ...,
             "frame-diff": 0.24
             },
       "1": {...},
       "2": {...},
       ...
}
'''



class SaveColorInfo:
    def __init__(self, inp_dir, out_dir):
        self.inp_dir = inp_dir
        self.out_dir = out_dir
        self.filelist = os.listdir(self.inp_dir)

    def cal_hist(self, frame, mask):
        # hist_all = []
        ave_all = []
        peak_all = []
        num_pix = len(mask.nonzero()[0])
        for ch in range(2, -1, -1):
            ave = np.sum(np.sum(frame[:, :, ch] * mask)) / num_pix
            ave_all.append(ave)
            # ave_all.append(np.around(ave, decimals=2))
            # ave_all.append("%.02f" % ave)
            peak = np.max(frame[:, :, ch] * mask).astype(np.float)
            peak_all.append(peak)

        luma = 0.0722 * frame[:, :, 0] + 0.7152 * frame[:, :, 1] + 0.2126 * frame[:, :, 2]

        ave = np.sum(np.sum(luma * mask)) / num_pix
        ave_all.append(ave)
        # ave_all.append(np.around(ave, decimals=2))
        # ave_all.append("%.02f" % ave)
        # print(ave_all)
        # print(peak_all)
        peak_all.append(np.max(luma * mask).astype(np.float))
        # print(peak_all[0].dtype, ave_all[0].dtype)
        return ave_all, peak_all

    def get_mask3(self, i, j):
        h_p, w_p = self.h / 3, self.w / 3
        mask_p = np.zeros([self.h, self.w], dtype=np.uint8)
        mask_p[ceil(h_p * i):floor(h_p * (i + 1)), ceil(w_p * j):floor(w_p * (j + 1))] = 1
        return mask_p

    def run(self):
        skip = 0
        for filename in self.filelist:
            skip += 1
            if skip == 1:
                continue
            print(filename)
            self.res = {}
            cap = cv2.VideoCapture(self.inp_dir + os.sep + filename)
            self.w, self.h = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            ret, frame = cap.read()
            frame_id = 0
            prev_frame = frame
            while frame is not None:
                self.res[frame_id] = {}

                ##### color histogram for the whole frame
                mask = np.ones([self.h, self.w], dtype=np.uint8)
                # print(self.h, self.w)
                ave, peak = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-all-ave"] = ave
                self.res[frame_id]["RGBL-all-peak"] = peak

                ##### color histogram on the 3x3 grids
                idxs = []
                for i in range(3):
                    for j in range(3):
                        idxs.append([i, j])
                items = ["RGBL-UL", "RGBL-UC", "RGBL-UR", "RGBL-ML", "RGBL-MC", "RGBL-MR", "RGBL-BL", "RGBL-BC", "RGBL-BR"]
                for idx, item in zip(idxs, items):
                    mask = self.get_mask3(idx[0], idx[1])
                    # cv2.imshow("mask", mask*255)  # check the masks
                    # cv2.waitKey(1000)
                    ave, peak = self.cal_hist(frame, mask)
                    self.res[frame_id]["%s-ave" % item] = ave
                    self.res[frame_id]["%s-peak" % item] = peak

                ##### color histogram on half of the image
                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[:, 0 : floor(self.w / 2)] = 1
                ave, peak = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-L-ave"] = ave
                self.res[frame_id]["RGBL-L-peak"] = peak

                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[:, ceil(self.w / 2):] = 1
                ave, peak = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-R-ave"] = ave
                self.res[frame_id]["RGBL-R-peak"] = peak

                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[0 : floor(self.h / 2), :] = 1
                ave, peak = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-U-ave"] = ave
                self.res[frame_id]["RGBL-U-peak"] = peak

                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[ceil(self.h / 2):, :] = 1
                ave, peak = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-B-ave"] = ave
                self.res[frame_id]["RGBL-B-peak"] = peak

                ##### color histogram on the central area
                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[floor(self.h * 0.25):ceil(self.h * 0.75), floor(self.w * 0.25):ceil(self.w * 0.75)] = 1
                ave, peak = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-C-ave"] = ave
                self.res[frame_id]["RGBL-C-peak"] = peak

                ##### frame difference
                if frame_id == 0:
                    ratio = -1
                else:
                    diff = frame - prev_frame
                    ratio = len(np.sum(diff, axis=2).nonzero()[0]) / (self.h * self.w)
                self.res[frame_id]["frame-diff"] = ratio
                # self.res[frame_id]["frame-diff"] = "%.02f" % ratio
                # print(ratio)
                prev_frame = frame

                # print(self.res[frame_id]["RGBL-all"][0])
                # print(frame_id)
                ret, frame = cap.read()
                frame_id += 1

                # break

            outname = self.out_dir + os.sep + os.path.basename(filename).split('.')[0] + os.sep + "color-opencv-raw.json"
            with open(outname, "w+") as write_f:
                json.dump(self.res, write_f)

            # break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_dir", required=True, help="input video file")
    parser.add_argument("--out_dir", required=True, help="directory to the output json file")
    args = vars(parser.parse_args())

    inp_dir = args["inp_dir"]
    out_dir = args["out_dir"]

    start = time.time()
    solver = SaveColorInfo(inp_dir, out_dir)
    solver.run()
    print(time.time() - start, "s in total.")

