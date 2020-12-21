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
    
    kubectl patch pod $HOSTNAME -n kubeflow -p '{"metadata": {"labels": {"app" : "object-detection-train-'${TIMESTAMP}'"}}}'
	
    cat >> object-detection-service-${TIMESTAMP}.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: object-detection-service-${TIMESTAMP}
  namespace: kubeflow
spec:
  selector:
    app: object-detection-train-${TIMESTAMP}
  type: NodePort
  ports:
    - protocol: TCP
      port: 8090
      targetPort: 8090
EOF

    #Create an external service to access the dynamic loss chart
    kubectl apply -f object-detection-service-${TIMESTAMP}.yaml -n kubeflow

    svc_port=$(kubectl get services -n kubeflow | grep object-detection-service-${TIMESTAMP} | awk '{print $5}')
    node_port=${svc_port#*:}
    node_port=${node_port%/*}

    echo "***********Loss mAP chart access details***********" > access_loss_chart.txt

    echo "" >> access_loss_chart.txt

    echo "Assigned node port for accessing loss chart is $node_port" >> access_loss_chart.txt

    echo "Please access dynamically plotted loss chart on http://<INGRESS/EXTERNAL IP>:$node_port" >> access_loss_chart.txt

    aws s3 cp access_loss_chart.txt ${S3_PATH}/access_loss_chart.txt

    sleep 10
   
    echo Training has started...
   
    # Training
    darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${gpus} -dont_show -mjpeg_port 8090 -map

    model_file_name=$(basename ${NFS_PATH}/backup/*final.weights)

    darknet detector map cfg/${CFG_DATA} cfg/${CFG_FILE} backup/$model_file_name > map_result.txt

    mv map_result.txt ./backup

    sleep 10

    # Delete the external service once training is completed
    kubectl delete -f object-detection-service-${TIMESTAMP}.yaml -n kubeflow

    rm -rf object-detection-service-${TIMESTAMP}.yaml

    mv chart.png chart-${TIMESTAMP}.png

    #Collect name of visualisation pod to copy the saved loss chart
    vis_podname=$(kubectl -n kubeflow get pods --field-selector=status.phase=Running | grep ml-pipeline-visualizationserver | awk '{print $1}')

    kubectl cp chart-${TIMESTAMP}.png $vis_podname:/src -n kubeflow

    mv chart*.png ./backup
   
   
else
    sed -i "s/momentum.*/momentum=${MOMENTUM}/g" cfg/${CFG_FILE}
    sed -i "s/decay.*/decay=${DECAY}/g" cfg/${CFG_FILE}

    # Training
    darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${GPUS} -dont_show > /var/log/katib/training.log
       
    cat /var/log/katib/training.log
    avg_loss=$(tail -2 /var/log/katib/training.log | head -1 | awk '{ print $3 }')
    echo "loss=${avg_loss}"
    

    if [[ -z "$avg_loss" ]]
    then
        echo "Darknet training has failed! Please check Katib trial pod error logs for detailed info at /var/log/katib/error.log"
        exit 2
    fi
fi
