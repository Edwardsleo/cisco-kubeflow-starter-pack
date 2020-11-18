#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--nfs_path")
       shift
       NFS_PATH="$1"
       shift
       ;; 
     "--saved_model_dir")
       shift
       MODEL_DIR="$1"
       shift
       ;;  
     "--trained_weights")
       shift
       TRAINED_WEIGHTS="$1"
       shift
       ;;
     "--classes_file")
       shift
       CLASSES_FILE="$1"
       shift
       ;;
     "--input_size")
       shift
       INPUT_SIZE="$1"
       shift
       ;;
     "--input_image")
       shift
       INPUT_IMAGE="$1"
       shift
       ;;
     "--tfrecord")
       shift
       TFRECORD="$1"
       shift
       ;;
     "--output_image")
       shift
       OUTPUT_IMAGE="$1"
       shift
       ;;
     "--num_classes")
       shift
       NUM_CLASSES="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd /opt/yolov3-tf2/

python3 detect.py  --trained_weights $NFS_PATH"/"$MODEL_DIR"/"$TRAINED_WEIGHTS --classes_file $NFS_PATH"/metadata/"$CLASSES_FILE --input_size $INPUT_SIZE --input_image $INPUT_IMAGE --tfrecord $TFRECORD --output_image $OUTPUT_IMAGE --num_classes $NUM_CLASSES

cp -r $OUTPUT_IMAGE $NFS_PATH"/"$MODEL_DIR
