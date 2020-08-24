"""
This script is used to give shot-level tagged annotation to the clips. The items to be tagged are assigned in
shot_tags.yaml, where all items are initially left None. Then the items which can be tagged from the detection
results pose-corrected-raw.json, shot-corrected-raw.json and frame-tagged-raw.json are updated using the
corresponding update functions in the class.

Example command: python 03_tag_shot.py --inp_dir E:\I3S\actorRepresentation\annotations\clip_06 --config \
E:\I3S\actorRepresentation\code\pose\shot_tags.yaml
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
        f_tag_frame = open(inp_dir + os.sep + r"frame-tagged-raw.json", "r")
        f_conf = open(config_file, "r")
        vid = r"../../dataset/" + os.path.basename(inp_dir) + ".mp4"
        cap = cv2.VideoCapture(vid)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        self.out_dir = out_dir
        self.config = yaml.load(f_conf, Loader=yaml.FullLoader)
        self.res_pose = json.load(f_pose)
        self.res_shot = json.load(f_shot)
        self.tag_frame = json.load(f_tag_frame)
        self.res = {}
        f_shot.close()
        f_pose.close()
        f_tag_frame.close()
        f_conf.close()

    def initiate(self):
        # Use res_shot to compose an empty res dict with all None except for frame_id and shot_id
        keys = list(self.config["SHOT-BOUNDARY"].keys())
        keys.extend(["primary-%s" % item for item in self.config["POSE-BASE"].keys()])
        keys.extend(["secondary-%s" % item for item in self.config["POSE-BASE"].keys()])
        vals = [None for i in range(len(keys))]
        for shot_id, dat in self.res_shot["shots"].items():
            self.res[int(shot_id)] = dict(zip(keys, vals))

    def update_duration(self, shot_id, dat):
        start_id = self.res_shot["shots"][str(shot_id)]["start_frame_id"]
        end_id = self.res_shot["shots"][str(shot_id)]["end_frame_id"]
        num_frames = end_id - start_id + 1
        duration = num_frames / self.fps

        self.res[shot_id]["duration-1s"] = False
        self.res[shot_id]["duration-2s"] = False
        self.res[shot_id]["duration-3s"] = False
        self.res[shot_id]["duration-5s"] = False
        self.res[shot_id]["duration-medium"] = False
        self.res[shot_id]["duration-long"] = False
        self.res[shot_id]["duration-very-long"] = False
        if duration <= 1:
            self.res[shot_id]["duration-1s"] = True
        elif duration <= 2:
            self.res[shot_id]["duration-2s"] = True
        elif duration <= 3:
            self.res[shot_id]["duration-3s"] = True
        elif duration <= 5:
            self.res[shot_id]["duration-5s"] = True
        elif duration <= 10:
            self.res[shot_id]["duration-medium"] = True
        elif duration <= 60:
            self.res[shot_id]["duration-long"] = True
        else:
            self.res[shot_id]["duration-very-long"] = True

    # def update_enter(self, shot_id, dat):
    #     shot_id = str(shot_id)
    #     start_id = str(self.res_shot["shots"][shot_id]["start_frame_id"])
    #     end_id = str(self.res_shot["shots"][shot_id]["end_frame_id"])
    #
    #     START_0 = self.tag_frame[start_id]["no-character"]
    #     END_0 = self.tag_frame[end_id]["no-character"]
    #     START_1 = self.tag_frame[start_id]["single-character"]
    #     END_1 = self.tag_frame[end_id]["single-character"]
    #
    #     if (START_0) and (not END_0):
    #         self.res[shot_id]["primary-enters"] = True
    #     else:
    #         self.res[shot_id]["primary-enters"] = False
    #     if (START_0 or START_1) and (not (END_0 or END_1)):
    #         self.res[shot_id]["secondary-enters"] = True
    #     else:
    #         self.res[shot_id]["secondary-enters"] = False


    # def update_exit(self, shot_id, dat): ## cases not complete
    #     shot_id = str(shot_id)
    #     start_id = str(self.res_shot["shots"][shot_id]["start_frame_id"])
    #     end_id = str(self.res_shot["shots"][shot_id]["end_frame_id"])
    #
    #     START_0 = self.tag_frame[start_id]["no-character"]
    #     END_0 = self.tag_frame[end_id]["no-character"]
    #     START_1 = self.tag_frame[start_id]["single-character"]
    #     END_1 = self.tag_frame[end_id]["single-character"]
    #
    #     if (not START_0) and (not END_0):
    #         self.res[shot_id]["primary-enters"] = True
    #     else:
    #         self.res[shot_id]["primary-enters"] = False
    #     if (START_0 or START_1) and (not (END_0 or END_1)):
    #         self.res[shot_id]["secondary-enters"] = True
    #     else:
    #         self.res[shot_id]["secondary-enters"] = False

    def update(self):
        for shot_id, dat in self.res_shot["shots"].items():
            shot_id = int(shot_id)
            # if self.res[shot_id].__contains__("primary-enters"):
            #     self.update_enter(shot_id, dat)
            if self.res[shot_id].__contains__("duration-1s"):
                self.update_duration(shot_id, dat)

    def save(self):
        with open(self.out_dir, "w+") as f_write:
            json.dump(self.res, f_write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_dir", required=True, help="path to corrected shot and pose json files")
    parser.add_argument("--config", required=True, help="configure yaml file")
    parser.add_argument("--out_dir", default="", help="path to output tagged shot json file")

    args = vars(parser.parse_args())
    inp_dir = args["inp_dir"]
    config = args["config"]
    out_dir = args["out_dir"]

    if out_dir == "":
        out_dir = inp_dir + os.sep + "shot-tagged-raw.json"

    tag = SaveTag(inp_dir, config, out_dir)
    tag.initiate()
    tag.update()
    tag.save()

