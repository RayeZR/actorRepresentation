import argparse
import os
import json
import csv

#

"""
res = {"command": "bash shot_batch.sh ffprobe ../../dataset ../../annotation 0.3",
       "toolname": "ffprobe",
       "params": {"threshold": threshold},
       "shots":
           {"0": {"start_frame_id": 000000, "end_frame_id": 000093, "prev_trans": "", "next_trans": ""}, 
            "1": {"start_frame_id": 000094, "end_frame_id": 000165, "prev_trans": "", "next_trans": ""}, 
            "2": {...},
            "3": {...},
            ...
           }
       }
"""


def main(command, inp_file, out_dir, threshold):
    res = {"command": command,
           "toolname": "ffprobe",
           "params": {"threshold": threshold},
           "shots": {}}
    with open(inp_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        frame_id = 0
        shot_id = 0
        for line in reader:
            if line[0] != "frame":
                continue
                #res["shots"][shot_id - 1]["end_frame_id"] += 1
                #break
            res["shots"][shot_id] = {}
            res["shots"][shot_id]["start_frame_id"] = frame_id
            frame_id = int(line[4].split('=')[1])
            res["shots"][shot_id]["end_frame_id"] = frame_id - 1
            res["shots"][shot_id]["prev_trans"] = ""
            res["shots"][shot_id]["next_trans"] = ""
            shot_id += 1
        #print(line)
        # print(reader)
        res["shots"][shot_id - 1]["end_frame_id"] += 1

    # out_name = out_dir + os.sep + "shot-ffprobe-%s-raw.json" % os.path.basename(inp_file).split('.')[0]
    out_name = out_dir + os.sep + "shot-ffprobe-raw.json"
    with open(out_name, 'w+') as write_f:
        json.dump(res, write_f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_file", required=True, help="path to openpose output json files")
    parser.add_argument("--out_dir", default="", help="path to output json file")
    parser.add_argument("--threshold", required=True, help="threshold")
    parser.add_argument("--cmd", required=True, help="Command used to generate the raw output")

    args = vars(parser.parse_args())
    inp_file = args["inp_file"]
    out_dir = args["out_dir"]
    threshold = args["threshold"]
    command = args["cmd"]

    if out_dir == "":
        out_dir = os.path.dirname(inp_file) + os.sep + "../.."

    main(command, inp_file, out_dir, threshold)
