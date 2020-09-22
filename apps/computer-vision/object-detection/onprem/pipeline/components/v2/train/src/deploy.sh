#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--nfs-path")
       shift
       NFS_PATH="$1"
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
     "--gpus")
       shift
       GPUS="$1"
       shift
       ;;
     "--momentum")
       shift
       MOMENTUM="$1"
       shift
       ;;
     "--decay")
       shift
       DECAY="$1"
       shift
       ;;
     "--component")
       shift
       COMPONENT="$1"
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

if [[ $COMPONENT == "train" || $COMPONENT == "TRAIN" ]]
then
    gpus=""
    for ((x=0; x < $GPUS ; x++ ))
    do
        if [[ $gpus == "" ]]
        then
                gpus="$x"
        else
                gpus="$gpus,$x"
        fi
    done
    # Training
    darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${gpus} -dont_show
else
    sed -i "s/momentum.*/momentum=${MOMENTUM}/g" cfg/${CFG_FILE}
    sed -i "s/decay.*/decay=${DECAY}/g" cfg/${CFG_FILE}
    # Training
    darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${GPUS} -dont_show > /var/log/katib/training.log
    cat /var/log/katib/training.log
    avg_loss=$(tail -2 /var/log/katib/training.log | head -1 | awk '{ print $3 }')
    echo "loss=${avg_loss}"
fi
