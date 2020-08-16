"""
Generate corrected shot-corrected-raw.json using the corrected shots, by reading and combining them into one.
Example command: python gen_corrected.py --inp_dir E:\I3S\actorRepresentation\annotations\clip_06\raw_output\pyscenedetect\split_raw \
--tool pyscenedetect
"""

import argparse
import os
import cv2
import json

def gen_corrected_json(inp_dir, out_dir, tool):
    file_list = sorted(os.listdir(inp_dir))
    # print(file_list)

    frame_id = -1
    shot_id = 0
    res = {"toolname": tool,
           "shots": {}}
    for filename in file_list:
        fullname = inp_dir + os.sep + filename
        cap = cv2.VideoCapture(fullname)
        ret, frame = cap.read()
        frame_id += 1
        res["shots"][shot_id] = {"start_frame_id": frame_id}
        while frame is not None:
            ret, frame = cap.read()
            frame_id += 1
        frame_id -= 1
        res["shots"][shot_id]["end_frame_id"] = frame_id
        res["shots"][shot_id]["prev_trans"] = ""
        res["shots"][shot_id]["next_trans"] = ""
        shot_id += 1

    out_name = out_dir + os.sep +"shot-corrected-raw.json"
    with open(out_name, 'w+') as write_f:
        json.dump(res, write_f)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--inp_dir", required=True, help="input video clips to be combined")
    parser.add_argument("--out_dir", default="", help="path to the output json file")
    parser.add_argument("--tool", required=True, help="toolname used")

    param = parser.parse_args()
    inp_dir = param.inp_dir
    out_dir = param.out_dir
    if out_dir == "":
        out_dir = inp_dir + "../../../.."
    tool = param.tool
    gen_corrected_json(inp_dir, out_dir, tool)