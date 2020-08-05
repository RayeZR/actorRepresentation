import argparse
import os

# inp_dir = r'E:\I3S\data\seg_01.txt'
# out_dir = r'e:\I3S\data\split_01.bat'


def get_split_points(seg_res):
    split_point = ["0"]
    with open(seg_res, 'r', encoding='utf-8') as inp_file:
        lines = inp_file.readlines()
        for line in lines:
            print(line)
            line_split = line.strip().split(',')
            if line_split[0] == "frame":
                for item in line_split:
                    if item.split("=")[0] == "pkt_pts_time":
                        split_point.append(item.split("=")[1])
    split_point.append("0")
    return split_point


# def write_script(inp_dir, split_point):
def write_script(inp, split_point):
    inp_filename = inp.split(os.sep)[-1].split('.')[0]
    if not os.path.exists(inp_filename):
        os.makedirs(inp_filename)
    bat_dir = 'gen_' + inp_filename + '.bat'

    with open(bat_dir, 'w+', encoding='utf-8') as bat_file:
        for i in range(len(split_point) - 1):
            writeline = 'ffmpeg -ss %s -to %s -accurate_seek -i %s -vcodec copy -acodec copy %s%s%s_shot_%02d.mp4\n' % (
            split_point[i], split_point[i + 1], inp, inp_filename, os.sep, inp_filename, i)
            bat_file.write(writeline)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--seg_res', type=str, required=True, help='input segment result file')
    parser.add_argument('--inp', type=str, required=True, help='input video file directory')

    param = parser.parse_args()
    inp = param.inp
    seg_res = param.seg_res

    split_points = get_split_points(seg_res)
    write_script(inp, split_points)