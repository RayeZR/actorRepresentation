import os
import json


# inp_dir = r"E:\I3S\actorRepresentation\code\histogram\03-Scene-016_L\\"
inp_dir = r"E:\I3S\actorRepresentation\code\output\openpose\01-Scene-017.json"
# with open(inp_dir, 'r') as f_load:
#     load_dict = json.load(f_load)
#     print(load_dict)
print(os.path.dirname(inp_dir))
print(os.path.basename(inp_dir))