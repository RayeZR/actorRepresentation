import numpy as np
from imutils import face_utils
import argparse
import imutils
import dlib
import cv2
import os

def detect(detector, predictor, filename, out_dir):
    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    [w, h] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    basename = os.path.basename(filename).split('.')[0]
    writer = cv2.VideoWriter(out_dir + os.sep + basename + '_res.avi', fourcc, fps, (w, h))

    ret, frame = cap.read()
    idx = 0
    while frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)

        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            (x, y, w, h) = face_utils.rect_to_bb(rect)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face #{}".format(i + 1), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            for (x, y) in shape:
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

        writer.write(frame)
        ret, frame = cap.read()
        idx += 1
        print(idx)

    cap.release()
    writer.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--predictor", required=True, help="path to facial landmark predictor")
    parser.add_argument("-i", "--input", required=True, help="path to input file")
    parser.add_argument("-o", "--out_dir", required=True, help="output directory")
    args = vars(parser.parse_args())

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["predictor"])

    filename = args["input"]
    out_dir = args["out_dir"]

    detect(detector, predictor, filename, out_dir)