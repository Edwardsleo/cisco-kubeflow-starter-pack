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
     "--cfg_data")
       shift
       CFG_DATA="$1"
       shift
       ;;
     "--timestamp")
       shift
       TIMESTAMP="$1"
       shift
       ;;
     "--user_namespace")
       shift
       USER_NAMESPACE="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

NFS_PATH=${NFS_PATH}/${TIMESTAMP}

# Download VOC datasets
aws s3 cp ${S3_PATH}/datasets ${NFS_PATH}/datasets --recursive
aws s3 cp ${S3_PATH}/cfg ${NFS_PATH}/cfg --recursive
aws s3 cp ${S3_PATH}/metadata ${NFS_PATH}/metadata --recursive
aws s3 cp ${S3_PATH}/pre-trained-weights ${NFS_PATH}/pre-trained-weights --recursive

cd ${NFS_PATH}

sed -i "s#metadata/#${NFS_PATH}/metadata/#g" cfg/${CFG_DATA}

backup_folder=$(awk '/backup/{print}' cfg/${CFG_DATA} | awk '{print$3}')

if  [[ $backup_folder = '.' ]]
then
    sed -i "5 s#\.#${NFS_PATH}/#g" cfg/${CFG_DATA}

elif ! [[ $backup_folder ]]
then
    sed -i  "5 s#\$#${NFS_PATH}#g" cfg/${CFG_DATA}

else
    mkdir -p $backup_folder
    sed -i "5 s#${backup_folder}#${NFS_PATH}/${backup_folder}#g" cfg/${CFG_DATA}
fi

data_folder_file=$(ls ${NFS_PATH}/datasets | grep .tar)
data_folder_name=${data_folder_file%.*}


sed -i "s#${data_folder_name}#${NFS_PATH}/datasets/${data_folder_name}#g" metadata/validate.txt
sed -i "s#${data_folder_name}#${NFS_PATH}/datasets/${data_folder_name}#g" metadata/train.txt

cd datasets

for f in *.tar; do tar xf "$f"; done

# Delete all tar files
rm -rf *.tar

copy_from_dir_name=${NFS_PATH#*/*/}
copy_to_dir_name=$(echo ${NFS_PATH} | awk -F "/" '{print $3}')
make_dir_name=exports/$copy_from_dir_name

# Copy datasets, weights and cfg into nfs-server in user namespace to be used for Katib
podname=$(kubectl -n ${USER_NAMESPACE} get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl exec -n ${USER_NAMESPACE} $podname  -- mkdir -p $make_dir_name
kubectl cp ${NFS_PATH} $podname:exports/$copy_to_dir_name -n ${USER_NAMESPACE}

