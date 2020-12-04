#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--nfs_path")
       shift
       NFS_PATH="$1"
       shift
       ;; 
     "--data_dir")
       shift
       DATA_DIR="$1"
       shift
       ;;
     "--image_list_file")
       shift
       IMAGE_LIST_FILE="$1"
       shift
       ;;  
     "--darknet_weights")
       shift
       WEIGHTS="$1"
       shift
       ;;
     "--converted_weights")
       shift
       CONVERTED_WEIGHTS="$1"
       shift
       ;;
     "--num_classes")
       shift
       NUM_CLASSES="$1"
       shift
       ;;
     "--dataset")
       shift
       DATASET="$1"
       shift
       ;;
     "--classes_file")
       shift
       CLASSES_FILE="$1"
       shift
       ;;
     "--transfer")
       shift
       TRANSFER="$1"
       shift
       ;;
     "--input-size")
       shift
       INPUT_SIZE="$1"
       shift
       ;;
     "--epochs")
       shift
       EPOCHS="$1"
       shift
       ;;
      "--batch_size")
       shift
       BATCH_SIZE="$1"
       shift
       ;;
     "--learning_rate")
       shift
       LEARNING_RATE="$1"
       shift
       ;;
     "--saved_model_dir")
       shift
       MODEL_DIR="$1"
       shift
       ;;
     "--samples")
       shift
       SAMPLES="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd /opt/yolov3-tf2/


python3 tools/voc-dataset-conversion.py --data_dir $NFS_PATH"/datasets/"$DATA_DIR --dataset $DATASET --image_list_file $NFS_PATH"/metadata/"$IMAGE_LIST_FILE --classes_file $NFS_PATH"/metadata/"$CLASSES_FILE
python3 convert.py --darknet_weights $NFS_PATH"/pre-trained-weights/"$WEIGHTS --converted_weights $CONVERTED_WEIGHTS --num_classes $NUM_CLASSES
python3 train.py --dataset $DATASET --converted_weights $CONVERTED_WEIGHTS --classes_file $NFS_PATH"/metadata/"$CLASSES_FILE --transfer $TRANSFER --input_size $INPUT_SIZE --epochs $EPOCHS --batch_size $BATCH_SIZE --learning_rate $LEARNING_RATE --saved_model_dir $MODEL_DIR --samples $SAMPLES 

cp -r $MODEL_DIR $NFS_PATH
