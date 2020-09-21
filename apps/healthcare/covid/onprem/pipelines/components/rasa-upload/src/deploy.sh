#!/bin/bash -e

set -x

while (($#)); do
   case $1 in
     "--minio_bucket")
       shift
       MINIO_BUCKET="$1"
       shift
       ;;
     "--minio_username")
       shift
       MINIO_USERNAME="$1"
       shift
       ;;
     "--minio_key")
       shift
       MINIO_KEY="$1"
       shift
       ;;
     "--minio_region")
       shift
       MINIO_REGION="$1"
       shift
       ;;
     "--model_name")
       shift
       MODEL_NAME="$1"
       shift
       ;;
     "--model_path")
       shift
       MODEL_PATH="$1"
       shift
       ;;
       
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd /opt
python3 minio_upload.py --minio_bucket ${MINIO_BUCKET} --minio_username ${MINIO_USERNAME} --minio_key ${MINIO_KEY} --minio_region ${MINIO_REGION} --model_name ${MODEL_NAME} --model_path ${MODEL_PATH}
