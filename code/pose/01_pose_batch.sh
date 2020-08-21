#!/bin/bash
tool=$1
inp_dir=$2
out_dir=$3
# bash 01_pose_batch.sh glib ../../dataset ../../annotations

command="bash 01_pose_batch.sh "$*
echo $command

if [ ! -d "$out_dir" ]; then
  mkdir -p $out_dir
fi

for file in `ls $inp_dir`
do
  filename=$(echo $file | cut -d . -f1)
  raw_output_dir=${out_dir}/${filename}/"raw_output"/${tool}
  if [ ! -d ${raw_output_dir} ]; then
    mkdir -p ${raw_output_dir}
  fi

  if [ $tool == "openpose" ]; then
    if [ $# -eq 4 ]; then
      expand=$4
    else
      expand=1.2
    fi
    echo "./build/examples/openpose/openpose.bin --video ${inp_dir}/${file} --write_video ${raw_output_dir}/${filename}-openpose-raw.avi --write_json ${raw_output_dir} --display 0 --face"
    ./build/examples/openpose/openpose.bin --video $inp_dir/$file --write_video ${raw_output_dir}/${filename}"-openpose-raw.avi" --write_json $raw_output_dir --display 0 --face

    echo "python3 01_format_openpose.py --inp_folder ${raw_output_dir} --expand $expand --cmd $command"
    python3 01_format_openpose.py --inp_folder ${raw_output_dir} --expand $expand --cmd "$command"
  fi

  if [ $tool == "glib" ]; then
    if [ $# -eq 4 ]; then
      model=$4
    else
      model="./model/shape_predictor_68_face_landmarks.dat"
      if [ ! -e $model ]; then
        echo "Default model file ./model/shape_predictor_68_face_landmarks.dat does not exist. Please input the directory to the model file as command line argument 4 or put it under the default directory."
      fi
    fi
    echo "Using model $model"
    echo "python3 01_run_and_format_glib.py --predictor $model --input_file ${inp_dir}/${file} --out_vid_dir ${raw_output_dir}/$filename"-glib-raw.avi" --out_json_dir ${out_dir}/${filename} --cmd $command"
    python3 01_run_and_format_glib.py --predictor $model --input_file ${inp_dir}/${file} --out_vid_dir ${raw_output_dir}/${filename}"-glib-raw.avi" --out_json_dir ${out_dir}/${filename} --cmd "$command"
  fi

done
