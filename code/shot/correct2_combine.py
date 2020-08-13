import cv2
import os
import argparse


def combine(inp_dir, inp_list):
    for combine_list in inp_list:
        name_list = combine_list.strip().split(' ')
        print(name_list)
        combine_num =len(name_list)
        cap = cv2.VideoCapture(inp_dir + os.sep + name_list[0] + ".avi")
        [w, h] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out_dir = inp_dir
        outname = '%s_join_%d.avi' % (name_list[0], combine_num)
        outname = out_dir + os.sep + outname
        writer = cv2.VideoWriter(outname, fourcc, fps, (w, h))

        for i in range(combine_num):
            filename = inp_dir + os.sep + name_list[i] + ".avi"
            cap = cv2.VideoCapture(filename)
            ret, frame = cap.read()
            while frame is not None:
                writer.write(frame)
                ret, frame = cap.read()
            cap.release()
            os.remove(filename)
        writer.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--inp_dir", required=True, help="input video clips to be combined")
    parser.add_argument("--combine", required=True, help="list of clips to be combined")

    param = parser.parse_args()
    inp_dir = param.inp_dir
    inp_list = list(param.combine.strip().split(','))
    combine(inp_dir, inp_list)

"""
--inp_dir
E:\I3S\actorRepresentation\annotations\clip_01\raw_output\pyscenedetect\split_raw
--combine
"005 006,014 015"

--inp_dir
E:\I3S\actorRepresentation\annotations\clip_02\raw_output\pyscenedetect\split_raw
--combine
"000 001 002, 003 004, 035 036, 042 043, 055 056 057_00, 057_01 057_02, 061 062 063_000, 066_001 066_002_000, 071 072_000, 076 077_00, 078 079_000_000, 079_000_001 079_000_002 079_001, 080 081 082_000_00, 083 084_000, 084_001 084_002 085_000, 085_001_00, 086_000 086_001_00, 087_000_001 087_001, 100 101 102 103 104"
"""