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

# Change darknet binary file to bin folder
mv ../darknet/darknet /usr/local/bin

cd ${NFS_PATH}

sed -i "s#/home/pjreddie/data/voc/#${NFS_PATH}/datasets/#g" cfg/${CFG_DATA}
cat cfg/${CFG_DATA}
sed -i "s#/home/pjreddie/backup/#${NFS_PATH}/backup#g" cfg/${CFG_DATA}
cat cfg/${CFG_DATA}
sed -i "s#data/#${NFS_PATH}/data/#g" cfg/${CFG_DATA}
cat cfg/${CFG_DATA}

# Update config file
sed -i 's/ batch.*/#batch=1/g' cfg/${CFG_FILE}
sed -i 's/ subdivisions.*/#subdivisions=1/g' cfg/${CFG_FILE}
sed -i 's/##batch.*/batch=64/g' cfg/${CFG_FILE}
sed -i 's/##subdivisions.*/subdivisions=16/g' cfg/${CFG_FILE}

if [[ $COMPONENT == "train" || $COMPONENT == "TRAIN" ]]
then
    momentum=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n anonymous -o=jsonpath='{.items[0].status.currentOptimalTrial.parameterAssignments[0].value}')
    decay=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n anonymous -o=jsonpath='{.items[0].status.currentOptimalTrial.parameterAssignments[1].value}')
    echo "MOMENTUN: $momentum"
    echo "DECY: $decay"
    sed -i "s/momentum.*/momentum=${momentum}/g" cfg/${CFG_FILE}
    sed -i "s/decay.*/decay=${decay}/g" cfg/${CFG_FILE}
    # Training
    darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${GPUS} -dont_show
else
    sed -i "s/momentum.*/momentum=${MOMENTUM}/g" cfg/${CFG_FILE}
    sed -i "s/decay.*/decay=${DECAY}/g" cfg/${CFG_FILE}
    darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${GPUS} -dont_show > /var/log/katib/training.log
    cat /var/log/katib/training.log
    avg_loss=$(sed -n '$p' /var/log/katib/training.log | awk '{ print $3 }')
    echo "loss=${avg_loss}"
fi
