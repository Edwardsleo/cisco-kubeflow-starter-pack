#!/bin/bash

set -x

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
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

NFS_PATH=${NFS_PATH}/${TIMESTAMP}

cd ${NFS_PATH}


#NFS Cleanup

#NFS Cleanup in kubeflow namespace
rm -rf backup cfg datasets metadata/*.txt  pre-trained-weights results validation-results

#NFS Cleanup in anonymous namespace
del_dir_name=exports/${NFS_PATH#*/*/}
nfspodname=$(kubectl -n anonymous get pods --field-selector=status.phase=Running | grep nfs-server | awk '{print $1}')
kubectl exec -n anonymous $nfspodname  -- rm -rf $del_dir_name


