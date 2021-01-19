#!/bin/bash

#Basic debugging mode
set -x

#Basic error handling
set -eo pipefail

while (($#)); do
   case $1 in
     "--nfs-path")
       shift
       NFS_PATH="$1"
        shift
       ;;
      "--cfg-file")
	shift
	CFG_FILE="$1"
	shift
	;;
      "--cfg_data")
       shift
       CFG_DATA="$1"
       shift
        ;;	
      "--weight-file")
        shift
        WEIGHT_FILE="$1"
        shift
	;;
      "--output")
        shift
        OUTPUT="$1"
        shift
        ;;
      "--patch-params")
        shift
        PATCH_PARAM="$1"
        shift
        ;;
      "--is-optimize")
        shift
        IS_OPTIMIZE="$1"
        shift
        ;;
      "--push-to-s3")
        shift
        PUSH_TO_S3="$1"
        shift
        ;;
      "--timestamp")
        shift
        TIMESTAMP="$1"
        shift
        ;;
      "--s3-path")
        shift
        S3_PATH="$1"
        shift
        ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done


NFS_PATH=${NFS_PATH}/${TIMESTAMP}

filename=$(basename -- "$CFG_FILE")
filename="${filename%.*}"

backup_folder=$(awk '/backup/{print}' ${NFS_PATH}/cfg/${CFG_DATA} | awk '{print$3}')

if [ ! -f ${NFS_PATH}/cfg/${CFG_FILE} ]; then
	echo "${filename}.cfg file is not present!"
	exit 1
fi

if [[ $backup_folder = '.' || $backup_folder = ' ' ]]
then 

if [ ! -f ${NFS_PATH}/${WEIGHT_FILE} ]; then
        echo "${filename}.weight file is not present!"
        exit 1
fi

else
if [ ! -f ${NFS_PATH}/${backup_folder}/${WEIGHT_FILE} ]; then
        echo "${filename}.weight file is not present!"
        exit 1
fi
fi

mkdir ${NFS_PATH}/ncnn-results

git clone https://github.com/xiangweizeng/darknet2ncnn.git

cd darknet2ncnn

git config --global http.proxy ''
git submodule init
git submodule update


cd darknet
make -j8
rm libdarknet.so
cd ../
echo "*********************Darknet build success*******"

cd ncnn
mkdir build 
cd build 
cmake ..
make -j8
make install
cd ../../
echo "*******************Ncnn build success***********"

make -j8

dos2unix ${NFS_PATH}/cfg/${CFG_FILE}


if [[ $backup_folder = '.' || $backup_folder = ' ' ]]
then

    ./darknet2ncnn ${NFS_PATH}/cfg/${CFG_FILE} ${NFS_PATH}/${WEIGHT_FILE} ${NFS_PATH}/ncnn-results/${filename}.param ${NFS_PATH}/ncnn-results/${filename}.bin
else
    ./darknet2ncnn ${NFS_PATH}/cfg/${CFG_FILE} ${NFS_PATH}/${backup_folder}/${WEIGHT_FILE} ${NFS_PATH}/ncnn-results/${filename}.param ${NFS_PATH}/ncnn-results/${filename}.bin
fi

if [[ ${IS_OPTIMIZE} == "True" || ${IS_OPTIMIZE} == "true" ]]
then
	ncnn/build/tools/ncnnoptimize ${NFS_PATH}/ncnn-results/${filename}.param ${NFS_PATH}/ncnn-results/${filename}.bin ${NFS_PATH}/ncnn-results/${filename}_opt.param ${NFS_PATH}/ncnn-results/${filename}_opt.bin 65536
	echo "audio is working"
fi


echo "********************************Conversion success*************"

cd ../
cd ../../

python opt/scripts/patchParam.py ${NFS_PATH}/ncnn-results/${filename}.param ${PATCH_PARAM}

if [[ ${PUSH_TO_S3} == "False" || ${PUSH_TO_S3} == "false" ]]
then
    echo Proceeding with cleanup of NFS

else
    if [[ ${PUSH_TO_S3} == "True" || ${PUSH_TO_S3} == "true" ]]
    then
	if [[ $backup_folder = '.' || $backup_folder = ' ' ]]
	then
	    weights_file=$(ls ${NFS_PATH}/*.weights)
	    weights_file_list=${weights_file[@]}

            for file in $weights_file_list
	    do	    
		aws s3 cp $file ${S3_PATH}/$(basename $file)
	    done

	    aws s3 cp ${NFS_PATH}/map_result.txt ${S3_PATH}
        else
	    aws s3 cp ${NFS_PATH}/${backup_folder} ${S3_PATH}/${backup_folder} --recursive
        fi	    
        aws s3 cp ${NFS_PATH}/ncnn-results ${S3_PATH}/ncnn-results --recursive
    else
        echo Please enter a valid input \(True/False\)
    fi
fi

