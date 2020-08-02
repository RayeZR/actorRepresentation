import argparse
import os
import json

"""
res = {"command": "bash pose_batch.sh tool inp_dir out_dir param",
       "toolname": "OpenPose",
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


def cal_on_screen_area(pose_kpts, face_kpts, ratio=1.2):
    x_list = [int(item) for item in [pose_kpts[3 * i] for i in range(len(pose_kpts) // 3)]]
    x_list.extend(int(item) for item in [face_kpts[3 * i] for i in range(len(face_kpts) // 3)])
    y_list = [int(item) for item in [pose_kpts[3 * i + 1] for i in range(len(pose_kpts) // 3)]]
    y_list.extend(int(item) for item in [face_kpts[3 * i + 1] for i in range(len(face_kpts) // 3)])
    x_list = [item for item in filter(lambda x: x != 0, x_list)]
    y_list = [item for item in filter(lambda x: x != 0, y_list)]

    x_max, x_min = max(x_list), min(x_list)
    y_max, y_min = max(y_list), min(y_list)
    area = (x_max - x_min) * (y_max - y_min) * ratio**2
   # print(x_max, x_min, y_max, y_min)
    return area


def main(command, inp_dir, out_dir, expand=1.2):
    filelist = sorted(os.listdir(inp_dir))
    res = {"command": command,
           "toolname": "OpenPose",
           "pose_kpts_id": POSE_BODY_25_BODY_PARTS,
           "params": {"expand_ratio": expand},
           "frames": {}}
    frame_id = 0
    for filename in filelist:
        if not filename.endswith(".json"):
            continue
        n_frame = int(filename.split('.')[0].split('_')[-2])
        assert frame_id == n_frame, "Global frame id = %d not equal to OpenPose output frame id = %d." %(frame_id, n_frame)
        file_path = inp_dir + os.sep + filename
        with open(file_path, 'r') as load_f:
            res["frames"][frame_id] = {}
            load_dict = json.load(load_f)
            # print(load_dict)
            for i, person in enumerate(load_dict["people"]):
                res_person = {"on_screen_area": 0, "pose_kpts": {}, "face_kpts": {}}
                pose_kpts = person["pose_keypoints_2d"]
                face_kpts = person["face_keypoints_2d"]

                n_kpts = int(len(pose_kpts) / 3)
                for kpt_id in range(n_kpts):
                    res_person["pose_kpts"][kpt_id] = [pose_kpts[3*kpt_id], pose_kpts[3*kpt_id+1], pose_kpts[3*kpt_id+2]]
                    if res_person["pose_kpts"][kpt_id][2] == 0:
                        res_person["pose_kpts"][kpt_id] = [-1, -1, -1]

                n_kpts = int(len(face_kpts) / 3)
                for kpt_id in range(n_kpts):
                    res_person["face_kpts"][kpt_id] = [face_kpts[3*kpt_id], face_kpts[3*kpt_id+1], face_kpts[3*kpt_id+2]]
                    if res_person["face_kpts"][kpt_id][2] == 0:
                        res_person["face_kpts"][kpt_id] = [-1, -1, -1]

                res_person["on_screen_area"] = cal_on_screen_area(pose_kpts, face_kpts)
                res["frames"][frame_id]["person_%02d" % i] = res_person
        frame_id += 1
    out_name = out_dir + os.sep + "pose-openpose-%s-raw.json" % os.path.basename(inp_dir)
    print(out_name, "has been generated.")
    with open(out_name, 'w+') as write_f:
        json.dump(res, write_f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_folder", required=True, help="path to openpose output json files")
    parser.add_argument("--out_dir", default="", help="path to output json file")
    parser.add_argument("--expand", default=1.2, help="on screen area expand ratio, default=1.2")
    parser.add_argument("--cmd", required=True, help="Command used to generate the raw output")

    args = vars(parser.parse_args())
    inp_folder = args["inp_folder"]
    out_dir = args["out_dir"]
    expand = args["expand"]
    command = args["cmd"]
    if out_dir == "":
        out_dir = inp_folder + os.sep + ".."

    main(command, inp_folder, out_dir, expand)

