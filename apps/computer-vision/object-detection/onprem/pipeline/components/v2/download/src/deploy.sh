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

for f in *.tar; do tar xf "$f"; done

# Delete all tar files
rm -rf *.tar

wget https://pjreddie.com/media/files/voc_label.py
python voc_label.py

cat 2007_train.txt 2007_val.txt 2012_*.txt > train.txt

# Copy datasets, weights and cfg into nfs-server in anonymous namespace to be used for katib
podname=$(kubectl -n anonymous get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl cp ${NFS_PATH} $podname:/exports -n anonymous
