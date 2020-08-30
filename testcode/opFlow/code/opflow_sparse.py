"""
Compute and save the sparse optical flow of a video clip.
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
    color = (0, 255, 0)
    winSize = round(min(size[0], size[1]) / 50)
    lk_params = dict(winSize=(winSize, winSize), maxLevel=2,
                     criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))
    prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
    feature_params = dict(maxCorners=300, qualityLevel=0.2, minDistance=2, blockSize=7)
    prev = cv.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
    mask = np.zeros_like(first_frame)

    while (cap.isOpened()):
        ret, frame = cap.read()
        if frame is not None:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            next, status, error = cv.calcOpticalFlowPyrLK(prev_gray, gray, prev, None, **lk_params)
            good_old = prev[status == 1]
            good_new = next[status == 1]
            line = ''
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                mask = cv.line(mask, (a, b), (c, d), color, 2)
                frame = cv.circle(frame, (a, b), 3, color, -1)
                line += "[%d %d %d %d]," % (c, d, a, b)
            # print(line)
            res.write(line[:-1] + '\n')
            output = cv.add(frame, mask)
            prev_gray = gray.copy()
            prev = good_new.reshape(-1, 1, 2)
            cv.imshow("sparse optical flow", output)
            writer.write(output)
            cv.waitKey(10)
        else:
            break
        # break
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
            print(file)
            extract_and_save_feature(inp_filename, out_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inp_dir', type=str, required=True, help='input video clips directory')
    parser.add_argument('--out_dir', type=str, required=True, help='output feature points directory')

    param = parser.parse_args()
    inp_dir = param.inp_dir
    out_dir = param.out_dir

    main(inp_dir, out_dir)