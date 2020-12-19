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
     "--timestamp")
       shift
       TIMESTAMP="$1"
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

NFS_PATH=${NFS_PATH}/${TIMESTAMP}

cd ${NFS_PATH}


#NFS Cleanup
del_dir_name=exports/${NFS_PATH#*/*/}


#NFS Cleanup in kubeflow namespace
kubeflow_nfspodname=$(kubectl -n kubeflow  get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl exec -n kubeflow  $kubeflow_nfspodname  -- rm -rf $del_dir_name

#NFS Cleanup in user's namespace
user_nfspodname=$(kubectl -n ${USER_NAMESPACE} get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl exec -n ${USER_NAMESPACE} $user_nfspodname  -- rm -rf $del_dir_name
