import json
import cv2

def load_file(inp_file):
    with open(inp_file, 'r') as file:
        load_dict = json.load(file)
        res = []
        num_people = len(load_dict['people'])
        for people in load_dict['people']:
            pose_kpts = people['pose_keypoints_2d']
            face_kpts = people['face_keypoints_2d']
            for i in range(0, len(face_kpts)//3):
                x, y, c = face_kpts[3*i], face_kpts[3*i+1], face_kpts[3*i+2]
                res.append([int(x), int(y), c])
        return res
                # if i == 0:
                #     return res
                # print(x, y, c)

if __name__ == '__main__':
    inp_file = r'E:\I3S\code\output\02-012\02-Scene-012_000000000000_keypoints.json'
    inp_vid = r'E:\I3S\code\test_data\02-Scene-012.mp4'
    load_file(inp_file)
    cap = cv2.VideoCapture(inp_vid)
    ret, frame = cap.read()
    res = load_file(inp_file)
    for (a, b, c) in res:
        print(a, b, c)
        frame = cv2.circle(frame, (a, b), 3, (0, 255, 0), -1)
        cv2.imshow("image", frame)
        cv2.waitKey(1000)
    cv2.waitKey(100000)