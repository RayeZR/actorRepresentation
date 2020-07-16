import cv2
import os

def main(inp_dir, out_file):
    cap = cv2.VideoCapture(inp_file)
    width, self.height = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = self.cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = os.path.splitext(inp_file)[0].split(os.sep)[-1]
    