#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--push-to-s3")
       shift
       PUSH_TO_S3="$1"
       shift
       ;;
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
     "--out-dir")
       shift
       OUT_PATH="$1"
       shift
       ;;
     "--input-size")
       shift
       INPUT_SIZE="$1"
       shift
       ;;
     "--model")
       shift
       MODEL="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd ${NFS_PATH}

git clone https://github.com/hunglc007/tensorflow-yolov4-tflite.git tensorflow_yolo

cd tensorflow_yolo
pip install -r requirements-gpu.txt

# Saved model
python3 save_model.py --weights ${NFS_PATH}/yolov3.weights  --output ${NFS_PATH}/${OUT_PATH} --input_size ${INPUT_SIZE} --model ${MODEL} --framework tflite

# Convert tensorflow model to tflite

python3 convert_tflite.py --weights ${NFS_PATH}/${OUT_PATH} --output ${NFS_PATH}/${OUT_PATH}/object_detection.tflite

if [[ $PUSH_TO_S3 == "False" || $PUSH_TO_S3 == "false" ]]
then
    echo Proceeding with Inference serving of the saved model in tflite format
else
    if [[ $PUSH_TO_S3 == "True" || $PUSH_TO_S3 == "true" ]]
    then
        aws s3 cp ${NFS_PATH}/${OUT_PATH} ${S3_PATH}/${OUT_PATH} --recursive
        aws s3 cp ${NFS_PATH}/backup ${S3_PATH}/backup --recursive
    else
        echo Please enter a valid input \(True/False\)
    fi
fi
