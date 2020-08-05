import cv2
import os
import argparse


def combine(inp_list, output):
    inp_num =len(inp_list)
    cap = cv2.VideoCapture(inp_list[0])
    [width, height] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    outdir = os.path.dirname(inp_list[0])
    if output == '':
        outname = os.path.splitext(inp_list[0])[0].split(os.sep)[-1] + '_join_%d.avi' % inp_num
    outname = outdir + os.sep + outname
    writer = cv2.VideoWriter(outname, fourcc, fps, (width, height))

    for i in range(inp_num):
        cap = cv2.VideoCapture(inp_list[i])
        ret, frame = cap.read()
        while frame is not None:
            writer.write(frame)
            ret, frame = cap.read()
        cap.release()
    writer.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", required=True, help="input video clips to be combined")
    parser.add_argument("-o", "--output", required=False, default='', help="output video")
    param = parser.parse_args()
    inp_list = param.input.strip().split(',')
    output = param.output
    combine(inp_list, output)

