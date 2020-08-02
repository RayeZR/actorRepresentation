from imutils import face_utils
import argparse
import dlib
import cv2
import os
import json

"""
res = {"command": "bash pose_batch.sh tool inp_dir out_dir param"
       "toolname": "Glib",
       "pose_kpts_id": POSE_BODY_25_BODY_PARTS, 
       "frames":
           {0: {"person_00": {"on_screen_area": 11.22, "pose_kpts": {0: [], 1: [], ...}, "face_kpts": {0: [], 1: [], ...}}, 
                "person_01": {"on_screen_area": 23.34, "pose_kpts": {0: [], 1: [], ...}, "face_kpts": {0: [], 1: [], ...}}
                },
            1: {"person_00": {"on_screen_area": 3.561, "pose_kpts": {0: [], 1: [], ...}, "face_kpts": {0: [], 1: [], ...}}, 
                "person_01": {"on_screen_area": 23.53, "pose_kpts": {0: [], 1: [], ...}, "face_kpts": {0: [], 1: [], ...}},
                "person_02": {"on_screen_area": 123.34, "pose_kpts": {0: [], 1: [], ...}, "face_kpts": {0: [], 1: [], ...}}
                },
            2: {...},
            3: {...},
            ...
           }
       }
"""

POSE_BODY_25_BODY_PARTS = {0: "Nose", 1: "Neck", 2: "RShoulder", 3: "RElbow", 4: "RWrist",
                           5: "LShoulder", 6: "LElbow", 7: "LWrist", 8: "MidHip", 9: "RHip",
                           10: "RKnee", 11: "RAnkle", 12: "LHip", 13: "LKnee", 14: "LAnkle",
                           15: "REye", 16: "LEye", 17: "REar", 18: "LEar", 19: "LBigToe",
                           20: "LSmallToe", 21: "LHeel", 22: "RBigToe", 23: "RSmallToe", 24: "RHeel",
                           25: "Background"}


def detect(command, detector, predictor, filename, out_vid_dir, out_json_dir):
    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    [w, h] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    basename = os.path.basename(filename).split('.')[0]
    writer = cv2.VideoWriter(out_vid_dir, fourcc, fps, (w, h))


    res = {"command": command,
           "toolname": "Glib",
           "pose_kpts_id": POSE_BODY_25_BODY_PARTS,
           "params": {},
           "frames": {}}
    frame_id = 0
    ret, frame = cap.read()
    while frame is not None:
        res["frames"][frame_id] = {}
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)
        for (i, rect) in enumerate(rects):
            res_person = {"on_screen_area": -1,
                          "pose_kpts": dict(zip([idx for idx in range(25)], [[-1, -1, -1] * 25])),
                          "face_kpts": {}}
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face #{}".format(i + 1), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            for (kpt_id, (x, y)) in enumerate(shape):
                res_person["face_kpts"][kpt_id] = [int(x), int(y), -1]
                #print(x.dtype, y.dtype)
                #print(x, y)
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
            res["frames"][frame_id]["person_%02d" % i] = res_person

        writer.write(frame)
        ret, frame = cap.read()
        frame_id += 1

    out_json_name = out_json_dir + os.sep + "pose-glib-%s-raw.json" % basename
    with open(out_json_name, 'w+') as write_f:
        json.dump(res, write_f)

    cap.release()
    writer.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictor", required=True, help="facial landmark predictor directory")
    parser.add_argument("--input_file", required=True, help="input file directory")
    parser.add_argument("--out_vid_dir", required=True, help="directory to output video")
    parser.add_argument("--out_json_dir", required=True, help="directory to output json file")
    parser.add_argument("--cmd", required=True, help="command used to generate the raw output")
    args = vars(parser.parse_args())

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["predictor"])

    filename = args["input_file"]
    out_vid_dir = args["out_vid_dir"]
    out_json_dir = args["out_json_dir"]
    command = args["cmd"]

    detect(command, detector, predictor, filename, out_vid_dir, out_json_dir)
