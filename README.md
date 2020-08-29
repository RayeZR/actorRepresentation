## Requirements and Instructions

### Workflow

####1. Code requirements

Dependencies for each tools (can be found in the tools part) + for the codes (`numpy`, `opencv-python`, `pyyaml`, `imutils`)

#### 2. Steps

1. (Optional) Preprocessing

   Remove the top and bottom fixed areas using `code/preprocessing.py`. The cropped video clip will be saved as `dataset/clip_xx_crop.avi`. It will be better to replace the original video in the `dataset` folder with the cropped one, in case of later auto-naming problems.

2. shot detection and correction

   0) use `ffprobe` or `pyscenedetect` (recommended) to produce the direct raw outputs.

   1) `01_format_raw_ffprobe.py` or `01_format_raw_pyscenedetect.py`: get the `shot-tool-raw.json`. 

   2) `02_check_raw.py`: split the original video clips into shots and manually check if the results are satisfied. If not, go back to step 0, change the threshold to get better results.

   3) `03_correct1_split.py`: split the shots which the tools are not able to split. This may introduce some FP.

   4) `04_correct2_combine.py`: combine the false shots that are split by the tools.

   5) `05_gen_corrected.py`: get the corrected shots `shot-corrected-raw.json`

3. color information

   `code/color/calc_color_info.py`: this gives `color-opencv-raw.json`. (No correction required since this only contains computation)

4. pose estimation

   1) use `openpose` and `glib` to produce the raw output (`01_pose_batch.sh`, or `openpose + 01_format_openpose.py`/`01_run_and_format_glib.py`)

   2) `02_correct_combine.py`: combine the raw output of openpose and glib to get `pose-corrected-raw.json`

5. tagged output

   1) `code/shot/03_tag_frame.py`: to give the frame-level tagged output `frame-tagged-raw.json`

   2) `code/shot/03_tag_shot.py`: to give the shot-level tagged output `shot-tagged-raw.json`

6. *camera estimation

   This requires to run voodoo camera on each separated shots that have been corrected. The 32-bit windows executable file is tested to be able to run under win10-x64.

 

### Shot Detection

#### 1. **ffprobe**

- setup: executable files for win, linux & macOS (also sourse code)

- documentation: https://ffmpeg.org/ffprobe.html  

- example command:`ffprobe -show_frames -of csv=s=,:nk=0 -f lavfi "movie=05.mp4, select=gt(scene\,0.2)" > seg_05.txt 2>&1 `

####	**2. PysceneDetect**

- setup: `pip install scenedetect`

- dependencies: opencv-python	

- documentation: https://pyscenedetect.readthedocs.io/en/latest/reference/command-lineparams/  
- example command: `scenedetect -i 01.mp4 detect-content list-scenes -n split-video -o 01\  `



### Pose Estimation

#### **1. OpenPose**

- homepage: https://github.com/CMU-Perceptual-Computing-Lab/openpose
- setup: the docker provided by the community (exsidius/openpose: https://github.com/gormonn/openpose-docker/blob/master/README.md) works well on the server
- example command: `./build/examples/openpose/openpose.bin --video ${inp_dir}/${file} --write_video ${raw_output_dir}/${filename}"-openpose-raw.avi" --write_json $raw_output_dir --display 0 --face`

#### **2. Dlib (or glib?)**

- setup: `pip install dlib`

- dependencies: some libraries: https://www.pyimagesearch.com/2017/03/27/how-to-install-dlib/ and `numpy` `scipy` `scikit-image` `imtuils` `opencv-python`

- detector: download from here https://github.com/AKSHAYUBHAT/TensorFace/blob/master/openface/models/dlib/shape_predictor_68_face_landmarks.dat (the one provided by the instruction raises some error)
- tutorial: https://www.pyimagesearch.com/2017/04/03/facial-landmarks-dlib-opencv-python/
- usage and raw output processing have been integrated in `code/pose/01_run_and_format_glib.py`