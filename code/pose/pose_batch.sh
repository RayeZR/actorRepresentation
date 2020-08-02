#!/bin/bash
tool=$1
inp_dir=$2
out_dir=$3

command="bash pose_batch.sh "$*
echo $command

if [ ! -d "$out_dir" ]; then
  mkdir $out_dir
fi

for file in `ls $inp_dir`
do
  filename=$(echo $file | cut -d . -f1)
  if [ ! -d ${out_dir}/${filename} ]; then
    mkdir ${out_dir}/${filename}
  fi

  if [ $tool == "openpose" ]; then
    if [ $# -eq 4 ]; then
      expand=$4
    else
      expand=1.2
    fi
    echo "./build/examples/openpose/openpose.bin --video ${inp_dir}/${file} --write_video ${out_dir}/${filename}/${filename}-openpose-raw.avi --write_json ${out_dir}/${filename} --display 0 --face"
    ./build/examples/openpose/openpose.bin --video $inp_dir/$file --write_video ${out_dir}/${filename}/${filename}"-openpose-raw.avi" --write_json $out_dir/$filename --display 0 --face

    echo "python3 format_openpose.py --inp_folder ${out_dir}/${filename} --expand $expand --cmd $command"
    python3 format_openpose.py --inp_folder ${out_dir}/${filename} --expand $expand --cmd "$command"
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
    echo "python3 run_and_format_glib.py --predictor $model --input_file ${inp_dir}/${file} --out_vid_dir ${out_dir}/$filename/$filename"-glib-raw.avi" --out_json_dir $out_dir --cmd $command"
    python3 run_and_format_glib.py --predictor $model --input_file ${inp_dir}/${file} --out_vid_dir ${out_dir}/${filename}/${filename}"-glib-raw.avi" --out_json_dir $out_dir --cmd "$command"
  fi

done
