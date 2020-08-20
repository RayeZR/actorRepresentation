import argparse
import os
import json
import yaml

"""
{0: {"frame-head": {"shot-id": 0, 
                    "no-character": False, 
                    "single-character": False, 
                    "two-shot": False, 
                    "three-shot": True,  // for this frame there are 3 characters
                    ... // general frame info
                    },
     "primary":   {"size-closeup": None, 
                   "size-medium": None, 
                   "size-long": None, 
                   "female": None, 
                   ... // both frame- and shot-level info
                  },
     "secondary": {"size-closeup": None, 
                   "size-medium": None, 
                   "size-long": None, 
                   "female": None, 
                   ... // both frame- and shot-level info, the same as primary character
                  },
     ... (scalable, wrt the number of characters)
     },
 1: {"frame-head": {...}, 
     "primary": {...} // e.g this is a frame with only 1 character
     },
 2: ...,
 ...
 }
 
"""


ORD = ["primary", "secondary"]


class SaveTag:
    def __init__(self, inp_dir, config_file, out_dir):
        f_pose = open(inp_dir + os.sep + r"pose-corrected-raw.json", "r")
        f_shot = open(inp_dir + os.sep + r"shot-corrected-raw.json", "r")
        f_conf = open(config_file, "r")
        self.config = yaml.load(f_conf, Loader=yaml.FullLoader)
        self.res_pose = json.load(f_pose)
        self.res_shot = json.load(f_shot)
        self.res = {}
        f_shot.close()
        f_pose.close()
        f_conf.close()

    def initiate(self):
        # Use res_shot to compose an empty res dict with all None except for frame_id and shot_id
        keys = list(self.config["FRAME-HEAD"].keys())
        keys.extend(list(self.config["SHOT-BOUNDARY"].keys()))
        for ord in ORD:
            keys.extend(["%s-%s" % (ord, item for item in self.config["POSE-BASE"].keys())])
        # keys.extend(["primary-%s" % item for item in self.config["POSE-BASE"].keys()])
        # keys.extend(["secondary-%s" % item for item in self.config["POSE-BASE"].keys()])
        vals = [None for i in range(len(keys))]
        for shot_id, dat in self.res_shot["shots"].items():
            start_frame = dat["start_frame_id"]
            end_frame = dat["end_frame_id"]
            for frame_id in range(start_frame, end_frame + 1):
                self.res[frame_id] = dict(zip(keys, vals))
                self.res[frame_id]["shot-id"] = shot_id
        # print(self.res)

    def update_character_number(self, frame_id, frame_dat):
        # Update the number of characters in a frame
        self.res[frame_id]["no-character"] = False
        self.res[frame_id]["single-character"] = False
        self.res[frame_id]["two-shot"] = False
        self.res[frame_id]["three-shot"] = False
        self.res[frame_id]["crowd-shot"] = False
        if len(frame_dat) == 0:
            self.res[frame_id]["no-character"] = True
        elif len(frame_dat) == 1:
            self.res[frame_id]["single-character"] = True
        elif len(frame_dat) == 2:
            self.res[frame_id]["two-shot"] = True
        elif len(frame_dat) == 3:
            self.res[frame_id]["three-shot"] = True
        else:
            self.res[frame_id]["crowd_shot"] = True

    def update_gender(self, frame_id, frame_dat):
        # Update gender (currently all are unknown)
        for ord in ORD:
            self.res[frame_id]["%s-gender-unknown" % ord] = True

    def update_face_direction(self, frame_id, ord_dat):
        # Update face orientation using if both eyes are detected or not
        for i, ord in enumerate(ORD):
            try:
                person = ord_dat[i][1]
            except IndexError:
                break
            leye, reye = [], []
            for kpt_id in range(36, 42):
                leye.extend(person[str(kpt_id)])
            leye.extend(person["68"])
            for kpt_id in range(42, 48):
                reye.extend(person[str(kpt_id)])
            reye.extend(person["69"])
            if set(leye) != -1 and set(reye) != -1:
                self.res[frame_id]["%s-face-forward" % ord] = True
                self.res[frame_id]["%s-face-backward" % ord] = False
            elif set(leye) == -1 and set(reye) == -1:    ## note: another possibility: face is too small so eyes are not detected !!!
                self.res[frame_id]["%s-face-forward" % ord] = False
                self.res[frame_id]["%s-face-backward" % ord] = True


    def update_legs(self, frame_id, ord_dat):
        # TODO



    def update(self):
        # Update the tagged items using res_pose
        for frame_id, dat in self.res_pose["frames"].items():
            if self.res[frame_id].__contains__("no-character"):
                self.update_character_number(frame_id, dat)
            if self.res[frame_id].__contains__("primary-gender-unknown"):
                self.update_gender(frame_id, dat)

            ordered_dat = sorted(dat.items(), key=lambda  d: d[1]["on_screen_area"])
            if self.res[frame_id].__contains__("primary-face-forward"):
                self.update_face_direction(frame_id, ordered_dat)
            if self.res[frame_id].__contains__("primary-legs-detected"):
                self.update_legs(frame_id, ordered_dat)


# def tag(inp_dir, config_file, out_dir):
#     f_pose = open(inp_dir + os.sep + r"pose-corrected-raw.json", "r")
#     f_shot = open(inp_dir + os.sep + r"shot-corrected-raw.json", "r")
#     f_conf = open(config_file, "r")
#     config = yaml.load(f_conf, Loader=yaml.FullLoader)
#     res_pose = json.load(f_pose)
#     res_shot = json.load(f_shot)
#     res = {}
#     # print(config)
#     keys = list(config["FRAME-HEAD"].keys())
#     keys.extend(list(config["SHOT-BOUNDARY"].keys()))
#     keys.extend(["primary-%s" % item for item in config["POSE-BASE"].keys()])
#     keys.extend(["secondary-%s" % item for item in config["POSE-BASE"].keys()])
#     vals = [None for i in range(len(keys))]
#
#     # Use res_shot to compose an empty res dict with all None except for frame_id and shot_id
#     for shot_id, data in res_shot["shots"].items():
#         start_frame = data["start_frame_id"]
#         end_frame = data["end_frame_id"]
#         for frame_id in range(start_frame, end_frame + 1):
#             res[frame_id] = dict(zip(keys, vals))
#             res[frame_id]["shot-id"] = shot_id
#     print(res)
#     f_shot.close()
#
#     for frame_id, data in res_pose["frames"].items():
#         if res[frame_id].__contains__("no-character"):


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_dir", required=True, help="path to corrected shot and pose json files")
    parser.add_argument("--config", required=True, help="configure yaml file")
    parser.add_argument("--out_dir", default="", help="path to output tagged frame json file")

    args = vars(parser.parse_args())
    inp_dir = args["inp_dir"]
    config = args["config"]
    out_dir = args["out_dir"]

    if out_dir == "":
        out_dir = inp_dir + os.sep + "frame-tagged-raw.json"
    tag(inp_dir, config, out_dir)

    # keys = ["01-%s" % item for item in TAG_DICT_BASE.keys()]
    # vals = [None for i in range(len(keys))]
    # primary = dict(zip(keys, vals))
    # print(primary)

