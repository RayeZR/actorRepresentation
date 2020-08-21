"""
This script is to correct the pose-tool-raw.json outputs by combining those from different tools together.
Currently is using the openpose output, when openpose detects no person but glib does, then integrate the glib results.

Example command: python 02_correct_combine.py --inp_dir E:\I3S\actorRepresentation\annotations\clip_06
"""

import argparse
import os
import json

def combine(inp_dir, out_dir):
    f_openpose = open(inp_dir + os.sep + "pose-openpose-raw.json", "r")
    res_openpose = json.load(f_openpose)
    f_glib = open(inp_dir + os.sep + "pose-glib-raw.json", "r")
    res_glib = json.load(f_glib)
    res = {"pose_kpts_id": res_openpose["pose_kpts_id"], "frames": {}}
    num_frames = len(res_openpose["frames"])
    for frame_id in range(num_frames):
        if res_openpose["frames"]["%s" % frame_id] == {}:
            print(res_glib["frames"]["%s" % frame_id])
            if res_glib["frames"]["%s" % frame_id] != {}:
                print("combine result from glib:")
                res_openpose["frames"]["%s" % frame_id] = res_glib["frames"]["%s" % frame_id]
                print(res_openpose["frames"]["%s" % frame_id])
        res["frames"]["%s" % frame_id] = res_openpose["frames"]["%s" % frame_id]
    with open(out_dir, "w+") as f_write:
        json.dump(res, f_write)
    f_openpose.close()
    f_glib.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_dir", required=True, help="path to pose raw json files to be combined")
    parser.add_argument("--out_dir", default="", help="path to output corrected json file")

    args = vars(parser.parse_args())
    inp_dir = args["inp_dir"]
    out_dir = args["out_dir"]

    if out_dir == "":
        out_dir = inp_dir + os.sep + "pose-corrected-raw.json"
    combine(inp_dir, out_dir)