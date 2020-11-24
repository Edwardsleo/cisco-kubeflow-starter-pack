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
     "--cfg_data")
       shift
       CFG_DATA="$1"
       shift
       ;;
     "--timestamp")
       shift
       TIMESTAMP="$1"
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
mkdir -p backup/${TIMESTAMP}

sed -i "s#metadata/#${NFS_PATH}/metadata/#g" cfg/${CFG_DATA}
sed -i "s#backup/#${NFS_PATH}/backup/${TIMESTAMP}#g" cfg/${CFG_DATA}

sed -i "s#voc-test#${NFS_PATH}/datasets/voc-test#g" metadata/validate.txt
sed -i "s#voc#${NFS_PATH}/datasets/voc#g" metadata/train.txt

cd datasets

for f in *.tar; do tar xf "$f"; done

# Delete all tar files
rm -rf *.tar

# Copy datasets, weights and cfg into nfs-server in anonymous namespace to be used for katib
podname=$(kubectl -n anonymous get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl cp ${NFS_PATH} $podname:/exports -n anonymous
