#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--nfs-path")
       shift
       NFS_PATH="$1"
       shift
       ;;
     "--s3-path")
       shift
       S3_PATH="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

# Download VOC datasets
aws s3 cp ${S3_PATH} ${NFS_PATH} --recursive

cd ${NFS_PATH}
mkdir -p backup

# Download Pre-trained weights
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov3.weights

cd datasets

tar xf VOCtrainval_11-May-2012.tar
tar xf VOCtrainval_06-Nov-2007.tar
tar xf VOCtest_06-Nov-2007.tar

wget https://pjreddie.com/media/files/voc_label.py
python voc_label.py

cat 2007_train.txt 2007_val.txt 2012_*.txt > train.txt
cd ..
sed -i 's#/home/pjreddie/data/voc/#/mnt/object_detection/datasets/#g' cfg/voc.data
sed -i 's#/home/pjreddie/backup/#/mnt/object_detection/backup#g' cfg/voc.data

# Update config file
sed -i 's/ batch=1/#batch=1/g' cfg/yolov3-voc.cfg
sed -i 's/ subdivisions=1/#subdivisions=1/g' cfg/yolov3-voc.cfg
sed -i 's/# batch=64/batch=64/g' cfg/yolov3-voc.cfg
sed -i 's/##subdivisions=16/subdivisions=16/g' cfg/yolov3-voc.cfg
