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
     "--component")
       shift
       COMPONENT="$1"
       shift
       ;;
     "--image")
       shift
       IMAGE="$1"
       shift
       ;;
     "--timestamp")
       shift
       TIMESTAMP="$1"
       shift
       ;;
      "--trials")
       shift
       TRIALS="$1"
       shift
       ;;
     "--gpus_per_trial")
       shift
       GPUS="$1"
       shift
       ;;
     "--user_namespace")
       shift
       USER_NAMESPACE="$1"
       shift
       ;;
     "--max_batches")
       shift
       MAX_BATCHES="$1"
       shift
       ;;
     "--experiment_spec")
       shift
       EXPERIMENT_SPEC="$1"
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

# update max_batches value in cfg file
#sed -i "s/max_batches.*/max_batches=$max/g" yolov3-voc.cfg
arrIN=(${CFG_FILE//./ })
katib_cfg="${arrIN[0]}-${TIMESTAMP}.${arrIN[1]}"
cp cfg/${CFG_FILE} cfg/${katib_cfg}
sed -i "s/max_batches.*/max_batches=${MAX_BATCHES}/g" cfg/${katib_cfg}

copy_from_dir_name=${NFS_PATH#*/*/}
copy_to_dir_name=$(echo ${NFS_PATH} | awk -F "/" '{print $3}')
make_dir_name=exports/$copy_from_dir_name

podname=$(kubectl -n ${USER_NAMESPACE} get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl cp cfg/${katib_cfg} $podname:exports/$copy_from_dir_name/cfg/${CFG_FILE} -n ${USER_NAMESPACE}


python3 ../../../../opt/experiment_launch.py --timestamp $TIMESTAMP --user_namespace $USER_NAMESPACE --image $IMAGE --nfs_path $NFS_PATH --trials $TRIALS --weights $WEIGHTS --cfg_file $CFG_FILE --cfg_data $CFG_DATA --gpus $GPUS --component_type $COMPONENT --experiment_spec $EXPERIMENT_SPEC

# Check katib experiment
kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE}

sleep 5

kubectl rollout status deploy/$(kubectl get deploy -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} | awk 'FNR==2{print $1}') -n ${USER_NAMESPACE}

yq r -P object-detection-$TIMESTAMP.yaml 'spec.parameters' > params.yaml

mkdir katib-${TIMESTAMP}

mv object-detection-${TIMESTAMP}.json object-detection-${TIMESTAMP}.yaml katib-${TIMESTAMP}

aws s3 cp katib-${TIMESTAMP} ${S3_PATH}/katib-${TIMESTAMP} --recursive

cat params.yaml | grep "name:" > param_names.txt

while read line
do

param_name=$(echo $line | awk  '{print $2}' | cut -c 3-)
param_names+=($param_name)

done <  param_names.txt

param_namelist=${param_names[@]}
echo "param_namelist ${param_namelist}"

params_count=$(cat params.yaml | grep "name:" | wc -l)

# Wait for katib experiment to succeed
while true
do
    status=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} | awk 'FNR==2{print $2}')
    if [[ $status == "Succeeded" ]]
    then
 
          for ((i=0;i<params_count;i++)); do
                    param_value=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} -o=jsonpath="{.items[0].status.currentOptimalTrial.parameterAssignments[$i].value}")
		    param_values+=($param_value)
          done

          param_valuelist=${param_values[@]}
	  echo "param_valuelist $param_valuelist"

	  actual_params_cnt=${#param_values[@]}

	  if [[ $actual_params_cnt < $params_count ]]
          then
              echo "Katib tuning has failed! Please check Katib trial pod logs for detailed info"
              exit 2
          else			
	      echo "Experiment: $status"
	      break
	  fi
    else
	if [[ -z "$status" ]]
        then
             echo "Status of Katib experiment not to be found!!"
	     exit 3
	else
	    echo "Experiment: $status"
	    sleep 30
	fi

    fi
done

for i in ${!param_names[@]}
do
  echo "${param_names[i]} : ${param_values[i]}" >> param_result.txt

  sed -i "s/${param_names[i]}.*/${param_names[i]}=${param_values[i]}/g" cfg/${CFG_FILE}

  echo "${param_names[i]} : ${param_values[i]}"
done  

#Cleanup

rm -rf katib-${TIMESTAMP} params.yaml param_names.txt param_result.txt
