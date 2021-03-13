#!/bin/bash

#Basic debugging mode
set -x

#Basic error handling
set -eo pipefail

# Retrieve names of user namespace and notebook server from notebook environment
IFS='/'
user_namespace=`echo $NB_PREFIX | awk '{print $2}'`
nbserver_name=`echo $NB_PREFIX | awk '{print $3}'` 
unset IFS

# Get User mail ID
read -p "Please enter mail ID for user $user_namespace: " user_mail


# Create service role binding YAML configuration file
touch service_role_binding.yaml

cat >> service_role_binding.yaml << EOF
apiVersion: rbac.istio.io/v1alpha1
kind: ServiceRoleBinding
metadata:
  name: bind-ml-pipeline-nb-#USER_NAMESPACE#
  namespace: kubeflow
spec:
  roleRef:
    kind: ServiceRole
    name: ml-pipeline-services
  subjects:
  - properties:
      source.principal: cluster.local/ns/#USER_NAMESPACE#/sa/default-editor
EOF


# Create envoy filter YAML configuration file 
touch envoy_filter.yaml

cat >> envoy_filter.yaml << EOF
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: add-header-#NBSERVER_NAME#
  namespace: #USER_NAMESPACE#
spec:
  configPatches:
  - applyTo: VIRTUAL_HOST
    match:
      context: SIDECAR_OUTBOUND
      routeConfiguration:
        vhost:
          name: ml-pipeline.kubeflow.svc.cluster.local:8888
          route:
            name: default
    patch:
      operation: MERGE
      value:
        request_headers_to_add:
        - append: true
          header:
            key: kubeflow-userid
            value: #USER_MAIL#
  workloadSelector:
    labels:
      notebook-name: #NBSERVER_NAME#
EOF

# Replace user namespace and notebook server name in YAML configuration files
sed -i "s/#USER_NAMESPACE#/$user_namespace/g" service_role_binding.yaml
sed -i -e "s/#NBSERVER_NAME#/$nbserver_name/g; s/#USER_NAMESPACE#/$user_namespace/g; s/#USER_MAIL#/$user_mail/g;" envoy_filter.yaml

# Apply the YAML files using kubectl
kubectl apply -f service_role_binding.yaml
kubectl apply -f envoy_filter.yaml

