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
     "--num_train_steps")
       shift
       NUM_TRAIN_STEPS="$1"
       shift
       ;;
     "--sample_1_of_n_eval_examples")
       shift
       SAMPLE_1_OF_N_EVAL_EXAMPLES="$1"
       shift
       ;;
   esac
done

echo $(pwd)
echo "****************************************************"

#cd object_detection/configs/tf2

#echo $(pwd)

#sed -i s#PATH_TO_BE_CONFIGURED/mobilenet_v2.ckpt-1#/mnt/tfrecord/mobilenet_v2/mobilenet_v2.ckpt-1#g ssd_mobilenet_v2_320x320_coco17_tpu-8.config

#sed -i s#PATH_TO_BE_CONFIGURED/label_map.txt#/models/research/object_detection/data/mscoco_label_map.pbtxt#g ssd_mobilenet_v2_320x320_coco17_tpu-8.config

#sed -i s#PATH_TO_BE_CONFIGURED/train2017-?????-of-00256.tfrecord#/mnt/tfrecord/coco_train.record-?????-of-00100#g ssd_mobilenet_v2_320x320_coco17_tpu-8.config

#sed -i s#PATH_TO_BE_CONFIGURED/val2017-?????-of-00032.tfrecord#/mnt/tfrecord/coco_val.record-?????-of-00050#g ssd_mobilenet_v2_320x320_coco17_tpu-8.config

#cat ssd_mobilenet_v2_320x320_coco17_tpu-8.config

#cd ../../../

#echo $(pwd)

#export PIPELINE_CONFIG_PATH="object_detection/configs/tf2/ssd_mobilenet_v2_320x320_coco17_tpu-8.config"
#echo $PIPELINE_CONFIG_PATH


NFS_PATH=${NFS_PATH}/${TIMESTAMP}

export PIPELINE_CONFIG_PATH="/mnt/object_detection1/pipeline.config"
echo $PIPELINE_CONFIG_PATH


python object_detection/model_main_tf2.py --model_dir=$NFS_PATH --num_train_steps=$NUM_TRAIN_STEPS --sample_1_of_n_eval_examples=$SAMPLE_1_OF_N_EVAL_EXAMPLES --pipeline_config_path=$PIPELINE_CONFIG_PATH 

