#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--nfs_path")
       shift
       NFS_PATH="$1"
       shift
       ;; 
     "--s3_path")
       shift
       S3_PATH="$1"
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
     "--push_to_s3")
       shift
       PUSH_TO_S3="$1"
       shift
       ;;
     "--tflite_model")
       shift
       TFLITE_MODEL="$1"
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

#Create tflite model from trained weights
python3 export_tflite.py --trained_weights $NFS_PATH"/"$MODEL_DIR"/"$TRAINED_WEIGHTS --tflite_model $NFS_PATH"/"$MODEL_DIR"/"$TFLITE_MODEL --classes_file $NFS_PATH"/metadata/"$CLASSES_FILE --num_classes $NUM_CLASSES --input_size $INPUT_SIZE


if [[ ${PUSH_TO_S3} == "False" || ${PUSH_TO_S3} == "false" ]]
then
    echo Proceeding with Inference serving of the saved model in tflite format...
    python3 infer_tflite.py --tflite_model $NFS_PATH"/"$MODEL_DIR"/"$TFLITE_MODEL --classes_file $NFS_PATH"/metadata/"$CLASSES_FILE --input_image $INPUT_IMAGE

else
    if [[ ${PUSH_TO_S3} == "True" || ${PUSH_TO_S3} == "true" ]]
    then
        aws s3 cp ${NFS_PATH}/${MODEL_DIR} ${S3_PATH}/${MODEL_DIR} --recursive
    else
        echo Please enter a valid input \(True/False\)
    fi
fi


