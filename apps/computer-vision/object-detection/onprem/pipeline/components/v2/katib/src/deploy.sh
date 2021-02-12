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

#copy_from_dir_name=${NFS_PATH#*/*/}
#copy_to_dir_name=$(echo ${NFS_PATH} | awk -F "/" '{print $3}')
#make_dir_name=exports/$copy_from_dir_name

#podname=$(kubectl -n ${USER_NAMESPACE} get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
#kubectl cp cfg/${katib_cfg} $podname:exports/$copy_from_dir_name/cfg/${CFG_FILE} -n ${USER_NAMESPACE}

touch object-detection-katib-$TIMESTAMP.yaml

cat >> object-detection-katib-$TIMESTAMP.yaml << EOF
apiVersion: kubeflow.org/v1alpha3
kind: Experiment
metadata:
  namespace: ${USER_NAMESPACE}
  labels:
    controller-tools.k8s.io: '1.0'
    timestamp: TIMESTAMP
  name: KATIB_NAME
spec:
  objective:
    type: minimize
    goal: 0.4
    objectiveMetricName: loss
  algorithm:
    algorithmName: random
  parallelTrialCount: 5
  maxTrialCount: NUMBER-OF-TRIALS
  maxFailedTrialCount: 3
  parameters:
  - name: "--momentum"
    parameterType: double
    feasibleSpace:
      min: '0.88'
      max: '0.92'
  - name: "--decay"
    parameterType: double
    feasibleSpace:
      min: '0.00049'
      max: '0.00052'
  trialTemplate:
    goTemplate:
      rawTemplate: |-
        apiVersion: batch/v1
        kind: Job
        metadata:
          name: {{.Trial}}
          namespace: {{.NameSpace}}
        spec:
          template:
            spec:
              containers:
              - name: {{.Trial}}
                image: docker.io
                command:
                - "/opt/deploy.sh"
                - "--nfs-path"
                - "/mnt/"
                - "--weights"
                - "PRETRAINED-WEIGHTS"
                - "--cfg_data"
                - "CONFIG-DATA"
                - "--cfg_file"
                - "CONFIG-FILE"
                - "--gpus"
                - "GPUS"
                - "--component"
                - "COMPONENT-TYPE"
                {{- with .HyperParameters}}
                {{- range .}}
                - "{{.Name}}"
                - "{{.Value}}"
                {{- end}}
                {{- end}}
                volumeMounts:
                - mountPath: /mnt
                  name: nfs-volume
                resources:
                  limits:
                    nvidia.com/gpu: GPU-PER-TRIAL
              restartPolicy: Never
              volumes:
              - name: nfs-volume
                persistentVolumeClaim:
                  claimName: nfs1
EOF


EXP_NAME="object-detection-$TIMESTAMP"
sed -i "s/KATIB_NAME/$EXP_NAME/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/TIMESTAMP/ts-$TIMESTAMP/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/NUMBER-OF-TRIALS/$TRIALS/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s|docker.io|$IMAGE|g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s#/mnt/#$NFS_PATH#g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/CONFIG-DATA/$CFG_DATA/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/CONFIG-FILE/$katib_cfg/g" object-detection-katib-$TIMESTAMP.yaml
#sed -i "s/CONFIG-FILE/$CFG_FILE/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/GPUS/$GPUS/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/COMPONENT-TYPE/$COMPONENT/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/GPU-PER-TRIAL/$GPUS/g" object-detection-katib-$TIMESTAMP.yaml

if [[ $WEIGHTS = 'None' || $WEIGHTS = 'none' ]]
then
     sed -i '/- "PRETRAINED-WEIGHTS"/d;/- "--weights"/d' object-detection-katib-$TIMESTAMP.yaml
else
     sed -i "s/PRETRAINED-WEIGHTS/$WEIGHTS/g" object-detection-katib-$TIMESTAMP.yaml
fi


# Creating katib experiment

kubectl apply -f object-detection-katib-$TIMESTAMP.yaml

sleep 1

# Check katib experiment
kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE}

sleep 5

kubectl rollout status deploy/$(kubectl get deploy -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} | awk 'FNR==2{print $1}') -n ${USER_NAMESPACE}

# Wait for katib experiment to succeed
while true
do
    status=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} | awk 'FNR==2{print $2}')
    if [ $status == "Succeeded" ]
    then
	  momentum=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} -o=jsonpath='{.items[0].status.currentOptimalTrial.parameterAssignments[0].value}')
          decay=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n ${USER_NAMESPACE} -o=jsonpath='{.items[0].status.currentOptimalTrial.parameterAssignments[1].value}')
	  if [[ -z "$momentum" || -z "$decay" ]]
	  then
              echo "Katib has failed! Please check Katib trial pod logs for detailed info"
              exit 2
          else			
	      echo "Experiment: $status"
	      break
	  fi
    else
	if [ -z "$status" ]
        then
             echo "Status of Katib experiment not to be found!!"
	     exit 3
	else
	    echo "Experiment: $status"
	    sleep 30
	fi

    fi
done


echo "MOMENTUM: $momentum"
echo "DECAY: $decay"

# Update momentun and decay in cfg file
sed -i "s/momentum.*/momentum=${momentum}/g" cfg/${CFG_FILE}
sed -i "s/decay.*/decay=${decay}/g" cfg/${CFG_FILE}
