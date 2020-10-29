#!/bin/bash

set -x

cd /opt/yolov3-tf2/

python3 tools/voc2012.py \
  --data_dir '/mnt/tfjob/VOCdevkit/VOC2012/' \
  --split train \
  --output_file ./data/voc2012_train.tfrecord

python3  tools/voc2012.py \
  --data_dir '/mnt/tfjob/VOCdevkit/VOC2012/' \
  --split val \
  --output_file ./data/voc2012_val.tfrecord

python3 convert.py
python3 train.py

cp -r trained_model/ /mnt/tfjob
cp -r checkpoints_keras/ /mnt/tfjob

