#!/bin/bash -e

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

# Get Ingress IP

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

# Create ClusterRoleBinding which provides access for user namespace's  serviceaccount  to connect with kubeflow namespace

kubectl create clusterrolebinding serviceaccounts-cluster-admin   --clusterrole=cluster-admin   --group=system:serviceaccounts
if [ $? -eq 0 ]; then
    echo "ClusterRoleBinding created succcessfully with name=serviceaccounts-cluster-admin "
elif [ `kubectl get clusterrolebinding  | grep serviceaccounts-cluster-admin | head -n1 | awk '{print $1;}'` = "serviceaccounts-cluster-admin" ]; then
    echo "ClusterRoleBinding already exists"
else
    echo "ClusterRoleBinding not created succcessfully, Please check permission"
    exit 1
fi


echo "**********Creation & installation setup on desired user namespaces**************"

while read usrdata
do

username=$(echo $usrdata | awk '{print $1}')
usernames+=($username)

done < users.txt

set -a
username_list=${usernames[@]}


#Undesired profiles cleanup
existing_users=$(kubectl get profiles --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')

for profile in $existing_users; do
    if ! [[ $profile = 'admin' ]]
    then     
        if ! [[ $username_list =~ (^|[[:space:]])$profile($|[[:space:]]) ]]
        then  
	      kubectl delete experiment -n $profile --all	
              kubectl delete pvc -n $profile --all 
                
              if [[ `kubectl get pv --template  '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}' | grep 'nfs-'$profile` = 'nfs-'$profile ]]
               then
                  #PV cleanup
                  kubectl delete pv 'nfs-'$profile
                  echo "PV of profile $profile deleted!"
              fi
               
              #Profile cleanup
              kubectl delete profile $profile 
                  echo "Profile $profile is deleted!"
            
              
         else
             echo "Profile $profile exists"
        fi
    fi
done

kubectl get configmap dex -n auth -o jsonpath='{.data.config\.yaml}' > dex-config.yaml

source add_static_users.sh

set +a

#Update ConfigMap dex
kubectl create configmap dex --from-file=config.yaml=dex-config.yaml -n auth --dry-run -oyaml | kubectl apply -f -

# Restart deployment dex to pick up the changes in the ConfigMap
kubectl rollout restart deployment dex -n auth


#Create desired user-profiles

while read usrdata
do 
    
    username=$(echo $usrdata | awk '{print $1}')
    storage=$(echo $usrdata | awk '{print $2}')
    #user_email=''
    #export user_email

    for email in $email_list
    do
       if [[ $email = ${username}* ]]
       then
           user_email=$email
       fi
    done

    if [[ `kubectl get profiles | grep $username | head -n1 | awk '{print $1;}'` = $username ]]
    then
    if [[ ! -z "$username" ]]
    then        
             echo "User profile $username already created/exists"
        else
         #echo "User profile name is null!"
         exit 1
        fi       
    else 
        echo "Creating user profile $username"

        cat >> user-profile.yaml << EOF
apiVersion: kubeflow.org/v1beta1
kind: Profile
metadata:
  name: $username   # replace with the name of profile you want, this will be user's namespace name
spec:
  owner:
    kind: User
    name: $user_email   # replace with the email of the user
EOF
    
        kubectl create -f user-profile.yaml
    
    if [ $? -eq 0 ]; then
        echo "$username profile created successfully"
    else
        echo "$username profile not created successfully"
        #rm -rf user-profile.yaml
        exit 1
    fi
    sleep 10

        rm -rf user-profile.yaml

    USER_NAMESPACE=`kubectl get namespace | grep $username | head -n1 | awk '{print $1;}'`
    if [[ "$USER_NAMESPACE" = $username ]]; then
        echo "$username namespace exists"
    else
        echo "$username namespace not created successfully and exiting"
                exit 1
    fi
    fi
        if ! [[ `kubectl get pods -n $username | grep nfs-server | awk '{print $1;}'` = 'nfs-server'* ]]
        then
           echo "Creating NFS server for $username namespace..."
       # Create nfs-server in user namespace
       kubectl apply -f nfs/nfs-server.yaml -n $username
       if [ $? -eq 0 ]; then
        echo "NFS server created successfully in $username namespace"
       else
        echo "NFS server not created successfully in $username namespace"
       fi
       sleep 5
        else
           echo "NFS server already exists in $username namespace"
        fi

    # Get NFS server ClusterIP
    NFS_USER_CLUSTER_IP=`kubectl -n $username get svc/nfs-server --output=jsonpath={.spec.clusterIP}`
    echo $NFS_USER_CLUSTER_IP
    if [ -z "${NFS_USER_CLUSTER_IP}" ]; then
        echo "NFS server svc in $username namespace is not created or assigned successfully"
        exit 1
    fi

        if ! [[ `kubectl get pv | grep nfs-${username} | awk '{print $1;}'` = 'nfs-'$username ]]
    then
            echo "Creating PV for $username namespace"
        cp nfs/nfs-pv.yaml nfs-user-pv.yaml

            #Replace IP
        # Updated sed command portable with linux(ubuntu) and macos
        sed -i.bak -e "s/nfs-cluster-ip/$NFS_USER_CLUSTER_IP/g; s/name: nfs/name: nfs-${username}/g; s/storage: 1Gi/storage: ${storage}/g" nfs-user-pv.yaml


        # Create NFS PV in user namespace
        kubectl apply -f nfs-user-pv.yaml
        if [ $? -eq 0 ]; then
        echo "PV for NFS server created successfully"
        else
        echo "PV for NFS server not created successfully"
        #revert_back
        exit 1
        fi
        sleep 5
            
        rm -rf nfs-user-pv.yaml.bak nfs-user-pv.yaml

        # Verify created PV
        kubectl get pv
 
    else
           echo "PV for $username namespace already exists!!"
        fi
    
        if ! [[ `kubectl get pvc -n $username | grep nfs-$username | awk '{print $1;}'` = 'nfs-'$username ]]
        then
            echo "Creating PVC for $username namespace..."
 
            #Replace PVC name
            cp nfs/nfs-pvc.yaml nfs-user-pvc.yaml
        sed -i.bak -e "s/name: nfs/name: nfs-${username}/g; s/storage: 1Gi/storage: ${storage}/g" nfs-user-pvc.yaml
    
    

        # Create NFS PVC in user namespace
        kubectl apply -f nfs-user-pvc.yaml -n $username
        if [ $? -eq 0 ]; then
         echo "PVC for NFS server created successfully in $username namespace"
        else
         echo "PVC for NFS server not created successfully in $username namespace"
         #revert_back
         exit 1
        fi
        sleep 5
    
        rm -rf nfs-user-pvc.yaml.bak nfs-user-pvc.yaml
    

        # Verify PVC in user namespace
        kubectl get pvc -n $username
         else
            echo "PVC for $username namespace already exists!!"
         fi 

     echo "NFS PV and PVC created in $username namespace"

done < users.txt

#Cleanup

rm -rf dex-config-numbered.yaml dex-config.yaml



