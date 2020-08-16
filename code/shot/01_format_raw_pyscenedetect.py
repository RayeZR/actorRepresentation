"""
This script is used to process the raw output of the tool pyscenedetect at the very beginning, and generate our desired
shot-pyscenedetect-raw.json. Expected output are as the following format:

res = {"command": "scenedetect -i S03E01.mp4 detect-content -t 30 list-scenes -o test-30\\",
       "toolname": "PySceneDetect",
       "params": {"threshold": threshold},
       "shots":
           {"0": {"start_frame_id": 000000, "end_frame_id": 000093, "prev_trans": "", "next_trans": ""},
            "1": {"start_frame_id": 000094, "end_frame_id": 000165, "prev_trans": "", "next_trans": ""},
            "2": {...},
            "3": {...},
            ...
           }
       }

Example commands are recorded at the end of the script (which are the ones used to generate the shot-tool-raw.json files).
"""

import argparse
import os
import json
import csv


def main(command, inp_file, out_dir, threshold):
    res = {"command": command,
           "toolname": "PySceneDetect",
           "params": {"threshold": threshold},
           "shots": {}}
    with open(inp_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        frame_id = 0
        cnt = 0
        for line in reader:
            cnt += 1
            if cnt <= 2:
                continue
            shot_id = int(line[0]) - 1
            res["shots"][shot_id] = {}
            res["shots"][shot_id]["start_frame_id"] = int(line[1])
            res["shots"][shot_id]["end_frame_id"] = int(line[4]) - 1
            res["shots"][shot_id]["prev_trans"] = ""
            res["shots"][shot_id]["next_trans"] = ""
            print(line)
        # print(reader)

    out_name = out_dir + os.sep + "shot-pyscenedetect-raw.json"
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

"""
commands (and params) used for 
--inp_file
E:\I3S\actorRepresentation\annotations\clip_01\raw_output\pyscenedetect\clip_01-Scenes.csv
--threshold
20
--cmd
"scenedetect -i clip_01.mp4 detect-content -t 20 list-scenes -o split-raw split-video -o split-raw"


--inp_file
E:\I3S\actorRepresentation\annotations\clip_02\raw_output\pyscenedetect\clip_02-Scenes.csv
--threshold
20
--cmd
"scenedetect -i clip_01.mp4 detect-content -t 20 list-scenes -o ./"


--inp_file
E:\I3S\actorRepresentation\annotations\clip_03\raw_output\pyscenedetect\clip_03-Scenes.csv
--threshold
30
--cmd
"scenedetect -i clip_03.mp4 detect-content -t 30 list-scenes -o ./"


--inp_file
E:\I3S\actorRepresentation\annotations\clip_04\raw_output\pyscenedetect\clip_04-Scenes.csv
--threshold
30
--cmd
"scenedetect -i clip_04.mp4 detect-content -t 30 list-scenes -o ./"


--inp_file
E:\I3S\actorRepresentation\annotations\clip_05\raw_output\pyscenedetect\clip_05-Scenes.csv
--threshold
10
--cmd
"scenedetect -i clip_05.mp4 detect-content -t 10 list-scenes -o ./"
"""