#!/bin/bash

#Install Kubeflow v1.1.0
export KF_APP="kf-app"
export KFDEF_URL="https://raw.githubusercontent.com/kubeflow/manifests/v1.1-branch/kfdef/kfctl_istio_dex.v1.1.0.yaml"
export KFCTL_URL="https://github.com/kubeflow/kfctl/releases/download/v1.1.0/kfctl_v1.1.0-0-g9a3621e_linux.tar.gz"
mkdir -p ${KF_APP}
cd ${KF_APP}
wget -O kfctl.tar.gz ${KFCTL_URL}
tar -zxvf kfctl.tar.gz
chmod +x kfctl
wget -O kfctl_k8s_istio.yaml ${KFDEF_URL}
./kfctl apply -V -f kfctl_k8s_istio.yaml
echo "The Kubeflow Central Dashboard is at ${INGRESS_IP}:31380"
