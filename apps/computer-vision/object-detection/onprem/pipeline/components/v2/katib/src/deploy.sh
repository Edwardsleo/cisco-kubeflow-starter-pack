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
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd ${NFS_PATH}

touch object-detection-katib-$TIMESTAMP.yaml

cat >> object-detection-katib-$TIMESTAMP.yaml << EOF
apiVersion: kubeflow.org/v1alpha3
kind: Experiment
metadata:
  namespace: anonymous
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

EXP_NAME="object-detection-$TIMESTAMP"
sed -i "s/KATIB_NAME/$EXP_NAME/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/TIMESTAMP/ts-$TIMESTAMP/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/NUMBER-OF-TRIALS/$TRIALS/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s|docker.io|$IMAGE|g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s#/mnt/#$NFS_PATH/#g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/PRETRAINED-WEIGHTS/$WEIGHTS/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/CONFIG-DATA/$CFG_DATA/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/CONFIG-FILE/$CFG_FILE/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/GPUS/$gpus/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/COMPONENT-TYPE/$COMPONENT/g" object-detection-katib-$TIMESTAMP.yaml
sed -i "s/GPU-PER-TRIAL/$GPUS/g" object-detection-katib-$TIMESTAMP.yaml


# Creating katib experiment

kubectl apply -f object-detection-katib-$TIMESTAMP.yaml

sleep 1

# Check katib experiment
kubectl get experiment -l timestamp=ts-$TIMESTAMP -n anonymous

kubectl rollout status deploy/$(kubectl get deploy -l timestamp=ts-$TIMESTAMP -n anonymous | awk 'FNR==2{print $1}') -n anonymous

# Wait for katib experiment Succeeded
while true
do
    status=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n anonymous | awk 'FNR==2{print $2}')
    if [ $status == "Succeeded" ]
    then
	    echo "Experiment: $status"
	    break
    else
	    echo "Experiment: $status"
	    sleep 30
    fi
done
momentum=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n anonymous -o=jsonpath='{.items[0].status.currentOptimalTrial.parameterAssignments[0].value}')
decay=$(kubectl get experiment -l timestamp=ts-$TIMESTAMP -n anonymous -o=jsonpath='{.items[0].status.currentOptimalTrial.parameterAssignments[1].value}')

echo "MOMENTUM: $momentum"
echo "DECAY: $decay"

# Update momentun and decay in cfg file
sed -i "s/momentum.*/momentum=${momentum}/g" cfg/${CFG_FILE}
sed -i "s/decay.*/decay=${decay}/g" cfg/${CFG_FILE}
