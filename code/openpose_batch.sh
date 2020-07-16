#!/bin/bash

inp_dir=$1
out_dir=$2

for file in `ls $inp_dir`
do
  filename=$(echo $file | cut -d . -f1)
  if [ ! -d "${out_dir}${filename}" ]; then
    mkdir ${out_dir}${filename}
  fi
  echo "./build/examples/openpose/openpose.bin --video ${inp_dir}${file} --write_json ${out_dir}${filename} --display 0 --face"
  ./build/examples/openpose/openpose.bin --video $inp_dir$file --write_video $out_dir${filename}/result.avi --write_json $out_dir$filename --display 0 --face
done
