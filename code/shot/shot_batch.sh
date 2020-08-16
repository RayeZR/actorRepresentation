#!/bin/bash
tool=$1
inp_dir=$2
out_dir=$3
# bash shot_batch.sh ffprobe ../../dataset ../../annotations

command="bash shot_batch.sh "$*
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

  # ffprobe -show_frames -of csv=s=,:nk=0 -f lavfi "movie=02.mp4, select=gt(scene\,0.15)" > seg_02.txt 2>&1
  # scenedetect -i S03E01.mp4 detect-content -t 30 list-scenes -o test-30\ split-video -o test-30\

  if [ $tool == "ffprobe" ]; then
    if [ $# -eq 4 ]; then
      threshold=$4
    else
      threshold=0.2
    fi
    echo "ffprobe -show_frames -of csv=s=,:nk=0 -f lavfi 'movie=${inp_dir}/${file}, select=gt(scene\,${threshold})' > ${raw_output_dir}/${filename}.txt 2>&1"
    ffprobe -show_frames -of csv=s=,:nk=0 -f lavfi "movie=${inp_dir}/${file}, select=gt(scene\,${threshold})" > ${raw_output_dir}/${filename}".txt" 2>&1

    echo "python3 format_ffprobe.py --inp_file ${raw_output_dir}/${filename}.txt --inp_vid ${inp_dir}/${file} --threshold $threshold --cmd $command"
    python3 format_ffprobe.py --inp_file ${raw_output_dir}/${filename}.txt --inp_vid ${inp_dir}/${file} --threshold $threshold --cmd "$command"
  fi

  if [ $tool == "pyscenedetect" ]; then
    if [ $# -eq 4 ]; then
      threshold=$4
    else
      threshold=30
    fi
    echo "scenedetect -i ${inp_dir}/${file} detect-content -t $threshold list-scenes -o ${raw_output_dir} split-video -o ${raw_output_dir}"
    scenedetect -i ${inp_dir}/${file} detect-content -t $threshold list-scenes -o ${raw_output_dir} split-video -o ${raw_output_dir}

    echo "python3 01_format_raw_pyscenedetect.py --inp_file ${raw_output_dir}/${filename}'-Scenes.csv' --threshold $threshold --cmd $command"
    python3 format_pyscenedetect.py --inp_file ${raw_output_dir}/${filename}"-Scenes.csv" --threshold $threshold --cmd "$command"
  fi
done
