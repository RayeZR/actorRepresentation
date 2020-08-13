import argparse
import os
import cv2
import json
import copy

def split(inp_json, inp_vid, out_dir):
    with open(inp_json, 'r') as load_f:
        anno = json.load(load_f)
    print(anno)
    shots = anno["shots"]
    key_frames = []
    for i in range(len(shots)):
        key_frames.append((shots[str(i)]["start_frame_id"], shots[str(i)]["end_frame_id"]))

    cap = cv2.VideoCapture(inp_vid)
    [w, h] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    shot_idx = 0
    frame_idx = 0
    write_cnt = 0
    ret, frame = cap.read()
    while frame is not None:
        frame_cp = copy.deepcopy(frame)
        if frame_idx == key_frames[shot_idx][0]:
            outname = out_dir + os.sep + "%03d.avi" % shot_idx
            writer = cv2.VideoWriter(outname, fourcc, fps, (w, h))

        if frame_idx == key_frames[shot_idx][1]:
            writer.write(frame)
            writer.release()
            shot_idx += 1
            cv2.putText(frame_cp, "shot #%d, frame #%d" % (shot_idx-1, frame_idx), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            cv2.putText(frame_cp, "shot #%d, frame #%d" % (shot_idx, frame_idx), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            writer.write(frame)

        # print(frame_idx)

        # cv2.imshow("vid", frame_cp)
        # try:
        #     if (frame_idx == key_frames[shot_idx][0]) or (frame_idx == key_frames[shot_idx-1][1]):
        #         cv2.waitKey(1000)
        #         # cv2.waitKey(1)
        #     else:
        #         cv2.waitKey(1)
        # except IndexError:
        #     break
        ret, frame = cap.read()
        frame_idx += 1

    cap.release()
    print("write_times:", write_cnt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_json", required=True, help="path to shot segmentation raw output json file")
    parser.add_argument("--inp_vid", required=True, help="path to original video file")
    parser.add_argument("--out_dir", default="", help="path to output raw video clips")
    parser.add_argument("--tool", required=True, help="tool name, ffprobe or pyscenedetect")

    args = vars(parser.parse_args())
    inp_json = args["inp_json"]
    inp_vid = args["inp_vid"]
    out_dir = args["out_dir"]
    tool = args["tool"]

    basename = os.path.basename(inp_vid).split('.')[0]
    if out_dir == "":
        out_dir = os.path.dirname(inp_vid) + os.sep + "../annotations/%s/raw_output/%s/split_raw" % (basename, tool)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    split(inp_json, inp_vid, out_dir)


"""
--inp_json
E:\I3S\actorRepresentation\annotations\clip_01\shot-pyscenedetect-raw.json
--inp_vid
E:\I3S\actorRepresentation\dataset\clip_01.mp4
--tool
pyscenedetect

--inp_json
E:\I3S\actorRepresentation\annotations\clip_02\shot-pyscenedetect-raw.json
--inp_vid
E:\I3S\actorRepresentation\dataset\clip_02.mp4
--tool
pyscenedetect
"""

