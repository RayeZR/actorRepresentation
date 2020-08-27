"""
This is the former script to save the color histogram information of the frames.
"""

import argparse
import os
import cv2
import numpy as np
from math import floor, ceil
import json
import time

'''
res = {"0": {"RGBL-all": [[1x256], [1x256], [1x256], [1x256]], "RGBL-all-ave": [1, 1, 1, 1],
             "RGBL-UL":  [[1x256], [1x256], [1x256], [1x256]], "RGBL-UL-ave":  [2, 1, 4, 5],
             "RGBL-UC":  ..., "RGBL-UC-ave": ...,
             ...
             "RGBL-C":   ..., "RGBL-C-ave": ...,
             "frame-diff": 0.24
             },
       "1": {...},
       "2": {...},
       ...
}
'''



class SaveHistogram:
    def __init__(self, inp_dir, out_dir, num_bins):
        self.inp_dir = inp_dir
        self.out_dir = out_dir
        self.num_bins = num_bins
        self.filelist = os.listdir(self.inp_dir)

    def cal_hist(self, frame, mask):
        hist_all = []
        ave_all = []
        num_pix = len(mask.nonzero()[0])
        for ch in range(2, -1, -1):
            hist = cv2.calcHist([frame], [ch], mask, [self.num_bins], [0, 255])
            hist = hist.reshape(256, )
            # cv2.normalize(hist, hist, 0, 255, cv2.NORM_L1)
            # hist_all.append(np.around(hist / sum(hist), decimals=2).tolist())
            hist = hist / sum(hist)
            hist_str = ','.join("%.02f" % item for item in hist)
            hist_all.append(hist_str)
            ave = np.sum(np.sum(frame[:, :, ch] * mask)) / num_pix
            # ave_all.append(np.around(ave, decimals=2))
            ave_all.append("%.02f" % ave)
        luma = 0.0722 * frame[:, :, 0] + 0.7152 * frame[:, :, 1] + 0.2126 * frame[:, :, 2]
        hist = cv2.calcHist([luma.astype(np.uint8)], [0], mask, [self.num_bins], [0, 255])
        hist = hist.reshape(256, )
        # cv2.normalize(hist, hist, 0, 255, cv2.NORM_L1)
        # hist_all.append(np.around(hist / sum(hist), decimals=2).tolist())
        hist = hist / sum(hist)
        hist_str = ','.join("%.02f" % item for item in hist)
        # print(hist_str)
        hist_all.append(hist_str)
        ave = np.sum(np.sum(luma)) / num_pix
        # ave_all.append(np.around(ave, decimals=2))
        ave_all.append("%.02f" % ave)
        # print(ave_all)
        return hist_all, ave_all

    def get_mask3(self, i, j):
        h_p, w_p = self.h / 3, self.w / 3
        mask_p = np.zeros([self.h, self.w], dtype=np.uint8)
        mask_p[ceil(h_p * i):floor(h_p * (i + 1)), ceil(w_p * j):floor(w_p * (j + 1))] = 1
        return mask_p

    def run(self):
        for filename in self.filelist:
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
                hist, ave = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-all"] = hist
                self.res[frame_id]["RGBL-all-ave"] = ave

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
                    hist, ave = self.cal_hist(frame, mask)
                    self.res[frame_id][item] = hist
                    self.res[frame_id]["%s-ave" % item] = ave

                ##### color histogram on half of the image
                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[:, 0 : floor(self.w / 2)] = 1
                hist, ave = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-L"] = hist
                self.res[frame_id]["RGBL-L-ave"] = ave

                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[:, ceil(self.w / 2):] = 1
                hist, ave = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-R"] = hist
                self.res[frame_id]["RGBL-R-ave"] = ave

                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[0 : floor(self.h / 2), :] = 1
                hist, ave = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-U"] = hist
                self.res[frame_id]["RGBL-U-ave"] = ave

                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[ceil(self.h / 2):, :] = 1
                hist, ave = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-B"] = hist
                self.res[frame_id]["RGBL-B-ave"] = ave

                ##### color histogram on the central area
                mask = np.zeros([self.h, self.w], dtype=np.uint8)
                mask[floor(self.h * 0.25):ceil(self.h * 0.75), floor(self.w * 0.25):ceil(self.w * 0.75)] = 1
                hist, ave = self.cal_hist(frame, mask)
                self.res[frame_id]["RGBL-C"] = hist
                self.res[frame_id]["RGBL-C-ave"] = ave

                ##### frame difference
                if frame_id == 0:
                    ratio = -1
                else:
                    diff = frame - prev_frame
                    ratio = len(np.sum(diff, axis=2).nonzero()[0]) / (self.h * self.w)
                # self.res[frame_id]["frame-diff"] = ratio
                self.res[frame_id]["frame-diff"] = "%.02f" % ratio
                # print(ratio)
                prev_frame = frame

                # print(self.res[frame_id]["RGBL-all"][0])
                # print(frame_id)
                ret, frame = cap.read()
                frame_id += 1

                # break

            outname = self.out_dir + os.sep + os.path.basename(filename).split('.')[0] + os.sep + "color-opencv-raw-str2.json"
            with open(outname, "w+") as write_f:
                json.dump(self.res, write_f)

            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_dir", required=True, help="input video file")
    parser.add_argument("--out_dir", required=True, help="directory to the output json file")
    parser.add_argument("--num_bins", default=256, help="number of bins to calculate the color histogram")
    args = vars(parser.parse_args())

    inp_dir = args["inp_dir"]
    out_dir = args["out_dir"]
    num_bins = args["num_bins"]

    start = time.time()
    solver = SaveHistogram(inp_dir, out_dir, num_bins)
    solver.run()
    print(time.time() - start, "s in total.")

