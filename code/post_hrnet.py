import os
import cv2
import numpy as np

name = '06_02'
ori_video = r"E:\I3S\actorRepresentation\code\test_data1\06-Scene-002.mp4"
root_dir = r"E:\I3S\actorRepresentation\hrnet\data\w32_512_adam_lr1e-3\\"
data_dir = r"E:\I3S\actorRepresentation\hrnet\data\test\%s\\" % name
res_dir = r"E:\I3S\actorRepresentation\hrnet\data\w32_512_adam_lr1e-3\%s\\" % name

data_files = sorted(os.listdir((data_dir)))
res_files = sorted(os.listdir(res_dir))


cap = cv2.VideoCapture(ori_video)
fps = cap.get(cv2.CAP_PROP_FPS)
[w, h] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
fourcc = cv2.VideoWriter_fourcc(*'XVID')
writer = cv2.VideoWriter(root_dir + '%s_combined_res.avi' % name, fourcc, fps, (w, h))
cap.release()

for i in range(len(res_files)):
    data = cv2.imread(data_dir + data_files[i])
    res = cv2.imread(res_dir + res_files[i])
    # print(np.max(res))
    # print(np.min(res))
    # print(data.shape)
    overlap = np.add(data, res)
    writer.write(overlap)
    # cv2.imshow("res", overlap)
    # cv2.waitKey(5)

    # print(res.shape)
writer.release()