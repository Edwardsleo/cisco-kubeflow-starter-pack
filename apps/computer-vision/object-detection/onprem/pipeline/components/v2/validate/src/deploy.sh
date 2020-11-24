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
     "--weights")
       shift
       WEIGHTS="$1"
       shift
       ;;
     "--cfg_data")
       shift
       CFG_DATA="$1"
       shift
       ;;
     "--cfg_file")
       shift
       CFG_FILE="$1"
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

cd ${NFS_PATH}

mkdir results

#Validation
darknet detector valid cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -dont_show

#Create directory with timestamp
mkdir -p validation-results/${TIMESTAMP}

#Copy results into timestamp directory
cp results/* validation-results/${TIMESTAMP}

#Push validation results to S3 bucket
aws s3 cp validation-results/${TIMESTAMP}  ${S3_PATH}/validation-results/${TIMESTAMP} --recursive

