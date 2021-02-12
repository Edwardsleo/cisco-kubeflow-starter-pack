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

# Check resources/GPU 
#namespace=$(kubectl get po --all-namespaces| grep $HOSTNAME | awk '{print $1}')
#node_name=$(kubectl get po $HOSTNAME -n $namespace -o=jsonpath={.spec.nodeName})
#node_des=$(kubectl describe node $node_name |  tr -d '\000' | sed -n -e '/^Name/,/Roles/p' -e '/^Capacity/,/Allocatable/p' -e '/^Allocated resources/,/Events/p'  | grep -e Name  -e  nvidia.com  | perl -pe 's/\n//'  |  perl -pe 's/Name:/\n/g' | sed 's/nvidia.com\/gpu:\?//g'  | awk '{print $2, $3}'  | column -t )
#total_gpus=$(echo $node_des | awk '{print $1}')
#used_gpus=$(echo $node_des | awk '{print $2}')
#current_available_gpus=$(expr $total_gpus - $used_gpus)
#if [[ $GPUS -gt $current_available_gpus ]];then
#        echo "Total GPU's in $node_name node: $total_gpus"
#        echo "Toatl used GPU's in $node_name node: $used_gpus"
#        echo "Current available GPU's in $node_name node:  $current_available_gpus"
#        echo "Requested $GPUS GPU's are not available in $node_name node."
#        exit 1
#fi

NFS_PATH=${NFS_PATH}/${TIMESTAMP}

cd ${NFS_PATH}

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

if [[ $COMPONENT == "train" || $COMPONENT == "TRAIN" ]]
then
    
    kubectl patch pod $HOSTNAME -n $USER_NAMESPACE -p '{"metadata": {"labels": {"app" : "object-detection-train-'${TIMESTAMP}'"}}}'

    cat >> object-detection-service-${TIMESTAMP}.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: object-detection-service-${TIMESTAMP}
  namespace: $USER_NAMESPACE
spec:
  selector:
    app: object-detection-train-${TIMESTAMP}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8090
EOF

    cat >> object-detection-virtualsvc-${TIMESTAMP}.yaml << EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: object-detection-virtualsvc-${TIMESTAMP}
  namespace: $USER_NAMESPACE
spec:
  gateways:
  - kubeflow/kubeflow-gateway
  hosts:
  - '*'
  http:
  - match:
    - uri:
        prefix: /${USER_NAMESPACE}/mapchart/${TIMESTAMP}
    rewrite:
      uri: /
    route:
    - destination:
        host: object-detection-service-${TIMESTAMP}.$USER_NAMESPACE.svc.cluster.local
        port:
          number: 80
    timeout: 300s
EOF

    #Create service to connect internally with training pod
    kubectl apply -f object-detection-service-${TIMESTAMP}.yaml -n $USER_NAMESPACE

    #Create virtual service to access dynamic loss cum mAP chart
    kubectl apply -f object-detection-virtualsvc-${TIMESTAMP}.yaml -n $USER_NAMESPACE 

    uri=$(sed -n '/prefix:/p' object-detection-virtualsvc-${TIMESTAMP}.yaml  | awk '{ print $2}')

    echo "***********Loss mAP chart access details***********" > access_loss_chart.txt

    echo "" >> access_loss_chart.txt

    echo "Assigned URI for accessing loss chart is $uri" >> access_loss_chart.txt

    echo "Please access dynamically plotted loss chart on http://<INGRESS/EXTERNAL IP>:<INGRESS_NODEPORT>$uri" >> access_loss_chart.txt

    aws s3 cp access_loss_chart.txt ${S3_PATH}/access_loss_chart.txt

    sleep 10
   
    echo Training has started...

    if [[ ${WEIGHTS} = 'None' || ${WEIGHTS} = 'none' ]]
    then

        # Train from scratch
        darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} -gpus ${gpus} -dont_show -mjpeg_port 8090 -map
    else
        # Train with pre-trained weights
        darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${gpus} -dont_show -mjpeg_port 8090 -map
    fi

    sleep 5

    # Delete service once training is completed
    kubectl delete -f object-detection-service-${TIMESTAMP}.yaml -n $USER_NAMESPACE

    rm -rf object-detection-service-${TIMESTAMP}.yaml

    # Delete virtual service
    kubectl delete -f object-detection-virtualsvc-${TIMESTAMP}.yaml -n $USER_NAMESPACE

    rm -rf object-detection-virtualsvc-${TIMESTAMP}.yaml


    backup_folder=$(awk '/backup/{print}' cfg/${CFG_DATA} | awk '{print$3}')

    
    model_file_name=$(basename ${backup_folder}/*final.weights)

    darknet detector map cfg/${CFG_DATA} cfg/${CFG_FILE} ${backup_folder}/$model_file_name > map_result.txt

    # Collect metrics for MLflow logging
    values_list=$(awk '/recall/{print}' map_result.txt | sed s/,/\\n/g)
    precision_score=$(echo $values_list | awk '{print $7}')
    recall_score=$(echo $values_list | awk '{print $10}')
    f1_score=$(echo $values_list | awk '{print $13}')
    map_line=$(awk '/mAP@/{print}' map_result.txt)
    map_value=$(echo $map_line | awk '{print $6}' | rev | cut -c2- | rev)

    echo "{\"metrics\": [{\"name\": \"f1-score\", \"numberValue\": ${f1_score}},{\"name\": \"precision-score\", \"numberValue\": ${precision_score}},{\"name\": \"recall-score\", \"numberValue\": ${recall_score}},{\"name\": \"map-score\", \"numberValue\": ${map_value}}]}" > /mlpipeline-metrics.json

    cat /mlpipeline-metrics.json
    
    if ! [[ -f ${backup_folder}/map_result.txt ]]

    then
          mv map_result.txt $backup_folder
    
    fi

    sleep 10

    mv chart.png chart-${TIMESTAMP}.png

    #Collect name of visualisation pod to copy the saved loss chart
    vis_podname=$(kubectl -n $USER_NAMESPACE get pods --field-selector=status.phase=Running | grep ml-pipeline-visualizationserver | awk '{print $1}')

    kubectl cp chart-${TIMESTAMP}.png $vis_podname:/src -n $USER_NAMESPACE

    if ! [[ -f ${backup_folder}/chart-${TIMESTAMP}.png ]]

    then 

         mv chart-${TIMESTAMP}.png $backup_folder 

    fi


else

    sed -i "s/momentum.*/momentum=${MOMENTUM}/g" cfg/${CFG_FILE}
    sed -i "s/decay.*/decay=${DECAY}/g" cfg/${CFG_FILE}

    if [[ ${WEIGHTS} = 'None' || ${WEIGHTS} = 'none' ]]
    then

        # Training from scratch
        #darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} -gpus ${gpus} -dont_show > /var/log/katib/metrics.log
        darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} -gpus ${gpus} -dont_show > /var/log/katib/training.log
    else
        # Training with pre-trained weights
        #darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${gpus} -dont_show > /var/log/katib/metrics.log
        darknet detector train cfg/${CFG_DATA} cfg/${CFG_FILE} pre-trained-weights/${WEIGHTS} -gpus ${gpus} -dont_show > /var/log/katib/training.log
    fi
       
    cat /var/log/katib/training.log
    avg_loss=$(tail -2 /var/log/katib/training.log | head -1 | awk '{ print $3 }')
    echo "loss=${avg_loss}"
    

    if [[ -z "$avg_loss" ]]
    then
        echo "Darknet training has failed! Please check Katib trial pod error logs for detailed info at /var/log/katib/error.log"
        exit 2
    fi
fi
