import cv2
import os
import numpy as np
import copy
import matplotlib.pyplot as plt


class Solver:
    def __init__(self, inp_file, out_dir):
        self.inp_file = inp_file
        self.cap = cv2.VideoCapture(inp_file)
        self.width, self.height = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        # self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        # self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.filename = os.path.splitext(inp_file)[0].split(os.sep)[-1]
        self.out_dir = out_dir + os.sep + self.filename
        self.rgb_dir = self.out_dir + '_RGB'
        self.l_dir = self.out_dir + '_L'
        if not os.path.exists(self.rgb_dir):
            os.makedirs(self.rgb_dir)
        if not os.path.exists(self.l_dir):
            os.makedirs(self.l_dir)

    def show_hist(self, hist, color):
        bin_count = hist.shape[0]
        bin_w = 1
        img = np.zeros((256, bin_count * bin_w, 3), np.uint8)
        for i in range(bin_count):
            h = int(hist[i])
            # cv2.rectangle(img, (i * bin_w + 2, 255), ((i + 1) * bin_w - 2, 255 - h), (int(180.0 * i / bin_count), 255, 255), -1)
            # cv2.rectangle(img, (i * bin_w + 2, 255), ((i + 1) * bin_w - 2, 255 - h), (255, 255, 255), -1)
            cv2.circle(img, (i, 255-h), 1, color, 2)
        # img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('hist', img)

    def get_hist(self, num_bin):
        channels = ("b", "g", "r")
        ret, frame = self.cap.read()
        f_id = 0
        while (frame is not None):
            mask = np.ones([self.height, self.width], dtype=np.uint8)
            fig = plt.figure()
            for ch in range(3):
                hist = cv2.calcHist([frame], [ch], mask, [num_bin], [0, 255])
                # cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
                plt.plot(hist, color=channels[ch], label=channels[ch])
                # self.show_hist(hist, colors[ch])
            plt.legend()
            # plt.show()
            fig.savefig(self.rgb_dir + os.sep + 'hist_rgb_%d.png' % f_id)
            plt.close(fig)

            fig = plt.figure()
            hist = cv2.calcHist([cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)], [2], mask, [num_bin], [0, 255])
            plt.plot(hist, color='c', label='V-HSV')

            hist = cv2.calcHist([cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)], [1], mask, [num_bin], [0, 255])
            plt.plot(hist, color='m', label='L-HSL')

            ave = (frame[:, :, 0] + frame[:, :, 1] + frame[:, :, 2]) / 3
            hist = cv2.calcHist([ave.astype(np.uint8)], [0], mask, [num_bin], [0, 255])
            plt.plot(hist, color='y', label='I-ave(R,G,B)')

            luma = 0.0722 * frame[:, :, 0] + 0.7152 * frame[:, :, 1] + 0.2126 * frame[:, :, 2]
            hist = cv2.calcHist([luma.astype(np.uint8)], [0], mask, [num_bin], [0, 255])
            plt.plot(hist, color='k', label='luma-HDTV(BT709)')

            plt.legend()
            # plt.show()
            fig.savefig(self.l_dir + os.sep + 'hist_l_%d.png' % f_id)
            plt.close(fig)

            f_id += 1
            ret, frame = self.cap.read()

        self.cap.release()



if __name__ == '__main__':
    inp_file = r'E:\I3S\actorRepresentation\code\test_data1\03-Scene-016.mp4'
    out_dir = r'E:\I3S\actorRepresentation\code\histogram'
    # num_bin = 16
    num_bin = 256
    solver = Solver(inp_file, out_dir)
    solver.get_hist(num_bin)