import argparse
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inp_dir", required=True, help="facial landmark predictor directory")
    parser.add_argument("--out_dir", required=True, help="input file directory")
    parser.add_argument("--num_bins", required=True, help="directory to output video")
    args = vars(parser.parse_args())

    filename = args["input_file"]
    out_vid_dir = args["out_vid_dir"]
    out_json_dir = args["out_json_dir"]
    command = args["cmd"]

    detect(command, detector, predictor, filename, out_vid_dir, out_json_dir)

