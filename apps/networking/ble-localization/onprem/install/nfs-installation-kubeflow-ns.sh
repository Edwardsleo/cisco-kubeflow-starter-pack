#!/bin/bash 

# Copyright 2018 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

echo "Provide Ingress IP (ex:10.123.232.211)"

read -p "INGRESS IP: " INGRESS_IP

echo $INGRESS_IP

if [ -z "${INGRESS_IP}" ]; then
  echo "You must specify Ingress IP"
  exit 1
fi

# Get Kubernetes cluster information

echo "Cluster Information"
kubectl cluster-info

if [ $? -eq 0 ]; then
    echo "kubectl is connected to K8s cluster"
else
    echo "kubectl is not connected to K8s cluster. Please update kubeconfig"
    exit 1
fi

echo "**********Installation setup on Kubeflow namespace**************"

KUBEFLOW_NAMESPACE=`kubectl get namespace | grep kubeflow | head -n1 | awk '{print $1;}'`

if [ "$KUBEFLOW_NAMESPACE" = "kubeflow" ]; then
    echo "Kubeflow namespace already exists"
else
    echo "Kubeflow namespace does not exist. Please check if Kubeflow is installed successfully in Kubeflow namespace"
    exit 1
fi

# Create ClusterRoleBinding which provides access for user namespace to connect with Kubeflow namespace

kubectl create clusterrolebinding serviceaccounts-cluster-admin  --clusterrole=cluster-admin  --group=system:serviceaccounts

if [ $? -eq 0 ]; then
    echo "ClusterRoleBinding created succcessfully with name=serviceaccounts-cluster-admin "
elif [ `kubectl get clusterrolebinding  | grep serviceaccounts-cluster-admin | head -n1 | awk '{print $1;}'` = "serviceaccounts-cluster-admin" ]; then
    echo "ClusterRoleBinding 'serviceaccounts-cluster-admin' already exists"    
else
    echo "ClusterRoleBinding 'serviceaccounts-cluster-admin' not created succcessfully. Please check permission"
    exit 1
fi
sleep 4

# Create secret for Kubeflow Dashboard IP

kubectl create secret generic kubeflow-dashboard-ip  --from-literal=KUBEFLOW_DASHBOARD_IP=$INGRESS_IP  -n kubeflow
sleep 4

# Check secrets in kubeflow ns
SECRET=`kubectl get secret -n kubeflow | grep kubeflow-dashboard-ip | head -n1 | awk '{print $1;}'`

if [ "$SECRET" = "kubeflow-dashboard-ip" ]; then
    echo "Secret 'kubeflow-dashboard-ip' is created successfully in Kubeflow namespace"
else
    echo "Secret 'kubeflow-dashboard-ip' is not created successfully"
    exit 1
fi

# Create NFS-server in Kubeflow  namespace
kubectl apply -f nfs/nfs-server.yaml -n kubeflow
sleep 5

# Retrieve NFS-server ClusterIP
NFS_KUBEFLOW_CLUSTER_IP=`kubectl -n kubeflow  get svc/nfs-server --output=jsonpath={.spec.clusterIP}`
echo $NFS_KUBEFLOW_CLUSTER_IP
if [ -z "${NFS_KUBEFLOW_CLUSTER_IP}" ]; then
    echo "NFS server service is not created or assigned successfully in Kubeflow namespace"
    exit 1
fi

cp nfs/nfs-pv.yaml nfs-kubeflow-pv.yaml

# Replace NFS-server IP placeholder with actual IP & storage requirement for PV
# Updated sed command portable with linux(ubuntu) and macOS
read -p "Enter storage resource for Kubeflow PV (Eg. 1Gi): " storage

sed -i.bak -e "s/nfs-cluster-ip/$NFS_KUBEFLOW_CLUSTER_IP/g; s/name: nfs/name: nfs-kubeflow/g; s/storage: 1Gi/storage: ${storage}/g" nfs-kubeflow-pv.yaml

# Create NFS PV in Kubeflow namespace
kubectl apply -f nfs-kubeflow-pv.yaml -n kubeflow
if [ $? -eq 0 ]; then
    echo "PV for NFS server created successfully"
else
    echo "PV for NFS server not created successfully"
    exit 1
fi
sleep 5

# Verify created PV 
kubectl get pv

#Clean up PV yaml files
rm -rf nfs-kubeflow-pv.yaml.bak nfs-kubeflow-pv.yaml

#Duplicate PVC yaml file
cp nfs/nfs-pvc.yaml nfs-kubeflow-pvc.yaml

sed -i.bak -e "s/name: nfs/name: nfs-kubeflow/g; s/storage: 1Gi/storage: ${storage}/g" nfs-kubeflow-pvc.yaml

# Create NFS PVC in Kubeflow namespace
kubectl apply -f nfs-kubeflow-pvc.yaml -n kubeflow
if [ $? -eq 0 ]; then
    echo "PVC for NFS server created successfully in Kubeflow namespace"
else
    echo "PVC for NFS server not created successfully in Kubeflow namespace"
    exit 1
fi
sleep 5

# Verify  PVC in Kubeflow namespace
kubectl get pvc -n kubeflow

#Clean up PVC yaml files
rm -rf nfs-kubeflow-pvc.yaml.bak nfs-kubeflow-pvc.yaml


echo "NFS PV and PVC created with name nfs-kubeflow in Kubeflow namespace"
