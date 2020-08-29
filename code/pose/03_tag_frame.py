"""
This script is used to give frame-level tagged annotation to the clips. The items to be tagged are assigned in
frame_tags.yaml, where all items are initially left None. Then the items which can be tagged from the detection
results pose-corrected-raw.json and shot-corrected-raw.json are updated using the corresponding update functions
in the class.

Example command: python 03_tag_frame.py --inp_dir E:\I3S\actorRepresentation\annotations\clip_06 --config \
E:\I3S\actorRepresentation\code\pose\frame_tags.yaml
"""

import argparse
import os
import json
import yaml
import cv2


ORD = ["primary", "secondary"]


class SaveTag:
    def __init__(self, inp_dir, config_file, out_dir):
        f_pose = open(inp_dir + os.sep + r"pose-corrected-raw.json", "r")
        f_shot = open(inp_dir + os.sep + r"shot-corrected-raw.json", "r")
        f_conf = open(config_file, "r")
        self.out_dir = out_dir
        self.config = yaml.load(f_conf, Loader=yaml.FullLoader)
        self.res_pose = json.load(f_pose)
        self.res_shot = json.load(f_shot)
        self.res = {}
        f_shot.close()
        f_pose.close()
        f_conf.close()

        basename = os.path.basename(inp_dir)
        vid_file = inp_dir + os.sep + r"../../dataset/" + basename + ".mp4"
        if not os.path.isfile(vid_file):
            vid_file = vid_file.replace(".mp4", "_crop.avi")
        if not os.path.isfile(vid_file):
            vid_file = vid_file.replace("_crop.avi", ".avi")
        vid = cv2.VideoCapture(vid_file)
        [w, h] = [int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))]
        vid.release()
        self.area = w * h


    def initiate(self):
        # Use res_shot to compose an empty res dict with all None except for frame_id and shot_id
        keys = list(self.config["FRAME-HEAD"].keys())
        keys.extend(list(self.config["SHOT-BOUNDARY"].keys()))
        # for ord in ORD:
        #     keys.extend(["%s-%s" % (ord, item for item in self.config["POSE-BASE"].keys())])
        keys.extend(["primary-%s" % item for item in self.config["POSE-BASE"].keys()])
        keys.extend(["secondary-%s" % item for item in self.config["POSE-BASE"].keys()])
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


    def update_size(self, frame_id, ord_dat):
        # Update character size
        for i, ord in enumerate(ORD):
            try:
                person = ord_dat[i][1]
            except IndexError:
                break
            self.res[frame_id]["%s-size-closeup" % ord] = False
            self.res[frame_id]["%s-size-medium" % ord] = False
            self.res[frame_id]["%s-size-long" % ord] = False
            person_area = person["on_screen_area"] / 1.44
            ratio = person_area / self.area
            if ratio > 0.4:
                self.res[frame_id]["%s-size-closeup" % ord] = True
            elif ratio > 0.2:
                self.res[frame_id]["%s-size-medium" % ord] = True
            else:
                self.res[frame_id]["%s-size-long" % ord] = True


    def update_gender(self, frame_id, ord_dat):
        # Update gender (currently all are unknown)
        for i, ord in enumerate(ORD):
            try:
                person = ord_dat[i][1]
            except IndexError:
                break
            self.res[frame_id]["%s-gender-unknown" % ord] = True
        # for ord in ORD:
        #     self.res[frame_id]["%s-gender-unknown" % ord] = True


    def update_face_direction(self, frame_id, ord_dat):
        # Update face orientation using if both eyes are detected or not
        for i, ord in enumerate(ORD):
            try:
                person = ord_dat[i][1]
            except IndexError:
                break
            leye, reye = [], []
            for kpt_id in range(36, 42):
                leye.extend(person["face_kpts"][str(kpt_id)])
            leye.extend(person["face_kpts"]["68"])
            for kpt_id in range(42, 48):
                reye.extend(person["face_kpts"][str(kpt_id)])
            reye.extend(person["face_kpts"]["69"])
            if set(leye) != {-1} and set(reye) != {-1}:
                self.res[frame_id]["%s-face-forward" % ord] = True
                self.res[frame_id]["%s-face-backward" % ord] = False
            elif set(leye) == {-1} and set(reye) == {-1}:    ## note: another possibility: face is too small so eyes are not detected !!!
                self.res[frame_id]["%s-face-forward" % ord] = False
                self.res[frame_id]["%s-face-backward" % ord] = True


    def update_head(self, frame_id, ord_dat):
        # Update head detection info
        for i, ord in enumerate(ORD):
            try:
                person = ord_dat[i][1]
            except IndexError:
                break
            head = []
            for kpt_id in range(15, 19):
                head.extend(person["pose_kpts"][str(kpt_id)])
            head.extend(person["pose_kpts"]["0"])
            for kpt_id in range(0, 70):
                head.extend(person["face_kpts"][str(kpt_id)])

            if set(head) != {-1}:
                self.res[frame_id]["%s-head-detected" % ord] = True
                self.res[frame_id]["%s-head-not-detected" % ord] = False
            else:
                self.res[frame_id]["%s-head-detected" % ord] = False
                self.res[frame_id]["%s-head-not-detected" % ord] = True


    def update_legs(self, frame_id, ord_dat):
        # Update leg detection info
        for i, ord in enumerate(ORD):
            try:
                person = ord_dat[i][1]
            except IndexError:
                # print(frame_id, i, "indexerror")
                break
            legs = []
            # print(i, person["pose_kpts"])
            for kpt_id in range(8, 15):
                legs.extend(person["pose_kpts"][str(kpt_id)])
            for kpt_id in range(19, 25):
                legs.extend(person["pose_kpts"][str(kpt_id)])
            if set(legs) != {-1}:
                self.res[frame_id]["%s-legs-detected" % ord] = True
                self.res[frame_id]["%s-legs-not-detected" % ord] = False
            else:
                self.res[frame_id]["%s-legs-detected" % ord] = False
                self.res[frame_id]["%s-legs-not-detected" % ord] = True


    def update(self):
        # Update the tagged items using res_pose
        for frame_id, dat in self.res_pose["frames"].items():
            frame_id = int(frame_id)
            # tag the general features
            if self.res[frame_id].__contains__("no-character"):
                self.update_character_number(frame_id, dat)

            # tag the features wrt primary and secondary characters
            ordered_dat = sorted(dat.items(), key=lambda  d: d[1]["on_screen_area"])
            if self.res[frame_id].__contains__("primary-size-closeup"):
                self.update_size(frame_id, ordered_dat)
            if self.res[frame_id].__contains__("primary-gender-unknown"):
                self.update_gender(frame_id, ordered_dat)
            if self.res[frame_id].__contains__("primary-face-forward"):
                self.update_face_direction(frame_id, ordered_dat)
            if self.res[frame_id].__contains__("primary-head_detected"):
                self.update_head(frame_id, ordered_dat)
            if self.res[frame_id].__contains__("primary-legs-detected"):
                self.update_legs(frame_id, ordered_dat)


    def save(self):
        with open(self.out_dir, "w+") as f_write:
            json.dump(self.res, f_write)


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

    tag = SaveTag(inp_dir, config, out_dir)
    tag.initiate()
    tag.update()
    tag.save()


