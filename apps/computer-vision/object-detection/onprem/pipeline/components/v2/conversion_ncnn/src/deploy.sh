#!/bin/bash

set -x
set -e

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

git clone https://github.com/xiangweizeng/darknet2ncnn.git

cd darknet2ncnn
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
./darknet2ncnn ${NFS_PATH}/cfg/${CFG_FILE} ${NFS_PATH}/backup/${WEIGHT_FILE} ${NFS_PATH}/${OUTPUT}/model.param ${NFS_PATH}/${OUTPUT}/model.bin


if [[ ${IS_OPTIMIZE} == "True" || ${IS_OPTIMIZE} == "true" ]]
then
	#echo "ncnn/build/tools/ncnnoptimize ${NFS_PATH}/${OUTPUT}/model.param ${NFS_PATH}/${OUTPUT}/model.bin audio_opt.param audio_opt.bin"
	echo "audio is working"
fi


echo "********************************Conversion success*************"

cd ../
cd ../../
python opt/scripts/patchParam.py ${NFS_PATH}/${OUTPUT}/model.param ${PATCH_PARAM}


if [[ ${PUSH_TO_S3} == "False" || ${PUSH_TO_S3} == "false" ]]
then
    echo Proceeding with Inference serving of the saved model in tflite format

else
    if [[ ${PUSH_TO_S3} == "True" || ${PUSH_TO_S3} == "true" ]]
    then
        aws s3 cp ${NFS_PATH}/backup ${S3_PATH}/backup --recursive
    else
        echo Please enter a valid input \(True/False\)
    fi
fi
