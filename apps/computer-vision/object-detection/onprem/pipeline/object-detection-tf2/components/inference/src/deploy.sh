#!/bin/bash

#Basic debugging mode
set -x

while (($#)); do
   case $1 in
     "--timestamp")
       shift
       TIMESTAMP="$1"
       shift
       ;;
     "--nfs-path")
       shift
       NFS_PATH="$1"
       shift
       ;;
   esac
done

echo $(pwd)

NFS_PATH=${NFS_PATH}/${TIMESTAMP}

cd $NFS_PATH
mkdir inference
cd ../../../

echo $pwd
cd /models/research

echo $(pwd)

export PIPELINE_CONFIG_PATH=$NFS_PATH/ssd_mobilenet_v2_320x320_coco17_tpu-8.config

python object_detection/export_tflite_graph_tf2.py --pipeline_config_path=$PIPELINE_CONFIG_PATH --trained_checkpoint_dir=$NFS_PATH --output_directory=$NFS_PATH/inference

sleep 10

echo $(pwd)
cd ../../
echo $(pwd)
python opt/tflite.py --saved_model_path=$NFS_PATH/inference/
