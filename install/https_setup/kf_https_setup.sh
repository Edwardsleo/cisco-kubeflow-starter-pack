#!/bin/bash

read -p "Enter the absolute path of your Kubeflow installation directory:  " kf_path

echo "$kf_path"

# Update Kubeflow gateway object with HTTPS related config

echo "******************Applying HTTPS config to Kubeflow gateway object************"
kubectl patch gateways.networking.istio.io kubeflow-gateway --patch "$(cat expose_https_port.yaml)" --type merge  -n kubeflow

echo

# Install Kustomize

echo "*****************Install Kustomize********************"
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
export PATH=$PATH:$PWD

echo

# Change directory to self-signed certificates configuration directory

cert_path=${kf_path}/.cache/manifests/manifests-1.1-branch/istio/ingressgateway-self-signed-cert/base
cd $cert_path

echo "**************Apply self-signed certficate configurations************"
kustomize build . | kubectl apply -f -


echo 

echo "Access Kubeflow's central dashboard on https://<INGRESS_IP>:31390"





