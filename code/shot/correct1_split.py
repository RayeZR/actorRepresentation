import cv2
import os
import numpy as np
import copy


class Solver:
    def __init__(self, inp_file):
        self.inp_file = inp_file
        self.cap = cv2.VideoCapture(inp_file)
        self.width, self.height = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.filename = os.path.splitext(inp_file)[0].split(os.sep)[-1]

    def show_hist(hist):
        bin_count = hist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count * bin_w, 3), np.uint8)
        for i in range(bin_count):
            h = int(hist[i])
            cv2.rectangle(img, (i * bin_w + 2, 255), ((i + 1) * bin_w - 2, 255 - h), (int(180.0 * i / bin_count), 255, 255),
                         -1)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('hist', img)

    def get_hist(self, num_bin):
        ret, frame = self.cap.read()
        self.features = []
        while (frame is not None):
            img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hue = img_hsv[:, :, 0]
            mask = np.ones([self.height, self.width], dtype=np.uint8)
            hist = cv2.calcHist([img_hsv], [0], mask, [num_bin], [0, 255])
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
            hist = hist.reshape(-1)
            self.features.append(hist)
            ret, frame = self.cap.read()
        print(len(self.features))
        # self.features.pop(-1) # remove the last frame

    def split_shots(self, num_center):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, self.labels, centers = cv2.kmeans(np.array(self.features), num_center, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        print("length: %d" % len(self.labels.reshape(-1)))
        # print(self.labels.reshape(-1))

    def correct_labels(self):
        num_frame = len(self.labels)
        for i in range(num_frame):
            if i == 0 or i == (num_frame - 1):
                continue
            if self.labels[i - 1] != self.labels[i] and self.labels[i] != self.labels[i + 1]:
                self.labels[i] = self.labels[i - 1]

    def write(self, out_dir):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.cap = cv2.VideoCapture(self.inp_file)
        idx = 0
        label = self.labels[0]
        writer = cv2.VideoWriter(os.path.join(out_dir, self.filename) + '_%02d.avi' % idx, self.fourcc, self.fps, (self.width, self.height))
        ret, frame = self.cap.read()
        i = 0
        info = '00.avi: '
        cnt = 0
        while frame is not None:
            if self.labels[i] == label:
                writer.write(frame)
                cnt += 1
                info += '%d ' % self.labels[i]
            else:
                idx += 1
                writer.release()
                writer = cv2.VideoWriter(os.path.join(out_dir, self.filename) + '_%02d.avi' % idx, self.fourcc, self.fps, (self.width, self.height))
                writer.write(frame)
                cnt += 1
                print(info)
                info = '%02d.avi: %d ' % (idx, self.labels[i])
            label = self.labels[i]
            # print(i)
            i += 1

            ret, frame = self.cap.read()
        writer.release()
        # print(cnt)



if __name__ == '__main__':
    # inp_file = r'E:\I3S\actorRepresentation\data\PySceneDetect\03\03-Scene-008.mp4'
    # inp_file = r'E:\I3S\actorRepresentation\annotations\clip_02\raw_output\pyscenedetect\split_raw\057.avi'
    inp_file = r"E:\I3S\actorRepresentation\annotations\clip_04\raw_output\pyscenedetect\split_raw\047_00_01.avi"
    out_dir = os.path.dirname(inp_file)
    # num_bin = 16
    num_bin = 256
    num_center = 2
    solver = Solver(inp_file)
    solver.get_hist(num_bin)
    solver.split_shots(num_center)
    solver.correct_labels()
    solver.write(out_dir)
    # os.remove(inp_file)