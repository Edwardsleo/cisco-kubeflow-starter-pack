#!/bin/bash

set -x

while (($#)); do
   case $1 in
     "--age")
       shift
       AGE="$1"
       shift
       ;;
     "--days")
       shift
       DAYS="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

echo "checking docker disk usage..."

docker system df

echo "Remove unused data
      This will remove:
        - all stopped containers
        - all networks not used by at least one container
	- all volumes not used by at least one container
        - all images without at least one container associated to them
        - all build cache"
docker system prune --all --force --volumes

echo "Check docker disk usage after removed unused data"
docker system df

echo "Delete files older than $DAYS days from nfs volume"
kubectl get ns | awk 'NR>1 {print $0}' | while read line; do
namespace=$(echo $line | awk '{print $1}')
podname=$(kubectl -n $namespace  get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
if [[ $podname != "" ]];then
    echo "List files older than $DAYS days"
    kubectl exec -n $namespace  $podname  -- find /exports -type f -mtime +$DAYS
    echo "Deleting files older than $DAYS days..."
    kubectl exec -n $namespace  $podname  -- find /exports -type f -mtime +$DAYS -exec rm -f {} \;
fi
done

echo "Delete katib experiments older than $AGE days"
kubectl get experiments --all-namespaces | awk 'NR>1 {print $0}' | while read line; do 
exp_name=$(echo $line | awk '{print $2}')
namespace=$(echo $line | awk '{print $1}')
age=$(echo $line | grep "$AGE" | awk '{print $4}')
if [ ! -z "$age" ]; then
    kubectl delete experiment $exp_name -n $namespace
fi
done

echo "Delete workflows older than $AGE days"
kubectl get workflows --all-namespaces | awk 'NR>1 {print $0}' | while read line; do
workflow_name=$(echo $line | awk '{print $2}')
namespace=$(echo $line | awk '{print $1}')
age=$(echo $line | grep "$AGE" | awk '{print $r3}')
if [ ! -z "$age" ]; then
    kubectl delete workflows $workflow_name -n $namespace
fi
done

echo "Delete .png files older than $DAYS days from visualization pod"
visu_podname=$(kubectl get po -l app=ml-pipeline-visualizationserver -n kubeflow | awk ' NR>1 {print $1}')
echo "List .png's older than $DAYS days"
kubectl exec -n kubeflow $visu_podname -- find -name "*.png" -type f -mtime +$DAYS
echo "Deleting .png's..."
kubectl exec -n kubeflow $visu_podname -- find -name "*.png" -type f -mtime +$DAYS -exec rm -f {} \;
