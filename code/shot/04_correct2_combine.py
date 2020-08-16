"""
Combine the wrongly split shots into a whole one.
Example command: python correct2_combine.py --inp_dir E:\I3S\actorRepresentation\annotations\clip_04\raw_output\pyscenedetect\split_raw
--combine "001 002 003 004 005 006 007, 047_00_00 047_00_01_00, 047_00_01_01 047_00_02 047_01 048"
(The shots to be combined are separated by ' ', and use ',' to separate multiple output clips)
"""

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
params used:
--inp_dir
E:\I3S\actorRepresentation\annotations\clip_01\raw_output\pyscenedetect\split_raw
--combine
"005 006,014 015"

--inp_dir
E:\I3S\actorRepresentation\annotations\clip_02\raw_output\pyscenedetect\split_raw
--combine
"000 001 002, 003 004, 035 036, 041_00 041_01, 042 043, 055 056 057_00, 057_01 057_02, 061 062 063_00, 066_01 066_02_00, 071 072_00, 073 074_00, 076 077_00, 078 079_00_00, 079_00_01 079_00_02 079_01, 080 081 082_00_00, 083 084_00 084_01_00, 084_01_01 084_02 085_00 085_01_00, 086_00 086_01_00, 087_00_01 087_01, 100 101 102 103 104"

--inp_dir
E:\I3S\actorRepresentation\annotations\clip_03\raw_output\pyscenedetect\split_raw
--combine
"007_00_00 007_00_01 007_00_02 007_00_03 007_00_04 007_00_05_00_00 007_00_05_00_01_00 007_00_05_00_01_01, 007_00_05_00_01_02 007_00_05_01 007_01, 038 039"

--inp_dir
E:\I3S\actorRepresentation\annotations\clip_04\raw_output\pyscenedetect\split_raw
--combine
"001 002 003 004 005 006 007, 047_00_00 047_00_01_00, 047_00_01_01 047_00_02 047_01 048"
"""