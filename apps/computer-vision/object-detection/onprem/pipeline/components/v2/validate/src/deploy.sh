#!/bin/bash

#Basic debugging mode
set -x

#Basic error handling
set -eo pipefail
shopt -s inherit_errexit

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
     "--trained_weights")
       shift
       TRAINED_WEIGHTS="$1"
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

NFS_PATH=${NFS_PATH}/${TIMESTAMP}

cd ${NFS_PATH}

mkdir results

backup_folder=$(awk '/backup/{print}' cfg/${CFG_DATA} | awk '{print$3}')


#Validation
darknet detector valid cfg/${CFG_DATA} cfg/${CFG_FILE} ${backup_folder}/${TRAINED_WEIGHTS} -dont_show

#Create directory with timestamp
mkdir -p validation-results

#Copy results into timestamp directory
cp results/* validation-results

#Push validation results to S3 bucket
aws s3 cp validation-results  ${S3_PATH}/validation-results --recursive
