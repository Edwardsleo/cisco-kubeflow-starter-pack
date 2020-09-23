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
      "--classes-file")
       shift
       CLASSES_FILE="$1"
       shift
       ;;
     "--tiny")
       shift
       TINY="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd ${NFS_PATH}

git clone https://github.com/peace195/tensorflow-lite-YOLOv3.git tensorflow_lite

if [ -d "$OUT_PATH" ]; then
  # Delete if folder exists
  rm -rf ${OUT_PATH}
fi

model_file_name=$(basename ${NFS_PATH}/backup/*final.weights)

if [[ ${TINY} == "False" || ${TINY} == "false" ]]
then
    python tensorflow_lite/convert_weights_pb.py --class_names ${NFS_PATH}/metadata/${CLASSES_FILE} --data_format NHWC --weights_file ${NFS_PATH}/backup/$model_file_name --output_graph ${NFS_PATH}/${OUT_PATH} --size=${INPUT_SIZE}
else
    if [[ ${TINY} == "True" || ${TINY} == "true" ]]
    then
        python tensorflow_lite/convert_weights_pb.py --class_names ${NFS_PATH}/metadata/${CLASSES_FILE} --data_format NHWC --weights_file ${NFS_PATH}/backup/$model_file_name --output_graph ${NFS_PATH}/${OUT_PATH} --size=${INPUT_SIZE} --tiny=${TINY}
    else
        echo Please enter a valid input \(True/False\)
    fi
fi

# Convert tensorflow model to tflite

tflite_convert --saved_model_dir=${NFS_PATH}/${OUT_PATH} --output_file=${NFS_PATH}/${OUT_PATH}/object_detection.tflite --saved_model_signature_key='predict'


if [[ ${PUSH_TO_S3} == "False" || ${PUSH_TO_S3} == "false" ]]
then
    echo Proceeding with Inference serving of the saved model in tflite format

else
    if [[ ${PUSH_TO_S3} == "True" || ${PUSH_TO_S3} == "true" ]]
    then
        aws s3 cp ${NFS_PATH}/${OUT_PATH} ${S3_PATH}/${OUT_PATH} --recursive
        aws s3 cp ${NFS_PATH}/backup ${S3_PATH}/backup --recursive
    else
        echo Please enter a valid input \(True/False\)
    fi
fi
