"""
Compute and save the dense optical flow of a video clip.
"""

import cv2 as cv
import numpy as np
import os
import argparse


def extract_and_save_feature(inp, out_dir):
    cap = cv.VideoCapture(inp)
    fps = cap.get(cv.CAP_PROP_FPS)
    size = (int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))

    fourcc = cv.VideoWriter_fourcc(*'XVID')
    writer = cv.VideoWriter(out_dir + os.sep + os.path.basename(inp).replace('.mp4', '.avi'), fourcc, fps, (size[0], size[1]))
    res = open(out_dir + os.sep + os.path.basename(inp).replace('.mp4', '.txt'), 'w+', encoding='utf-8')

    ret, first_frame = cap.read()
    winSize = round(min(size[0], size[1]) / 50)
    prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
    mask = np.zeros_like(first_frame)
    mask[..., 1] = 255

    while (cap.isOpened()):
        ret, frame = cap.read()
        if frame is not None:
            cv.imshow("input", frame)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, winSize, 3, 5, 1.2, 0)
            magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])
            mask[..., 0] = angle * 180 / np.pi / 2
            mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)
            rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)
            cv.imshow("dense optical flow", rgb)
            prev_gray = gray
            writer.write(rgb)
            cv.waitKey(10)
        else:
            break

    res.close()
    cap.release()
    writer.release()
    cv.destroyAllWindows()


def main(inp_dir, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    files = os.listdir(inp_dir)
    for file in files:
        if file.endswith(".mp4"):
            inp_filename = inp_dir + os.sep + file
            extract_and_save_feature(inp_filename, out_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inp_dir', type=str, required=True, help='input video clips directory')
    parser.add_argument('--out_dir', type=str, required=True, help='output feature points directory')

    param = parser.parse_args()
    inp_dir = param.inp_dir
    out_dir = param.out_dir

    main(inp_dir, out_dir)