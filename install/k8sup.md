# Installing Prerequisites


- [Docker](#docker)
    * [GPU Support](#gpu)
- [Kubernetes](#kubernetes)
- [Create a Kubernetes cluster](#k8s-up)
    * [Create cluster with kubeadm](#kubeadm)
    * [Set KUBECONFIG](#kubeconfig)
    * [Install cluster add-ons](#add-ons)
        - [Calico](#calico)
        - [NVIDIA Device Plugin](#nvidia)
        - [Storage Class](#rancher)
- [Check cluster readiness](#k8s-ready)

## Prerequisites 

* Cisco UCS - C240M5 and C480ML
* Ubuntu 16+ baremetal
* Nvidia 
   - Driver Version >= 410.129
   - CUDA Version		>= 10.0
   - nvidia-smi Version >= 410.129

## <a id=docker></a> Docker setup

Update and install common libraries
```bash
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    apache2-utils \
    ca-certificates \
    curl \
    software-properties-common \
    gnupg2
```

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88
# the output should equal:
# 9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable"

sudo apt-get update

sudo apt-get install -y \
  containerd.io=1.2.10-3 \
  docker-ce=5:18.09.3~3-0~ubuntu-bionic  \
  docker-ce-cli=5:18.09.3~3-0~ubuntu-bionic
```

[Source](https://kubernetes.io/docs/setup/production-environment/container-runtimes/#docker)

### <a id=gpu></a>GPU Support

Install nvidia-docker2

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```
Enable nvidia runtime as your default runtime on your node by editing the docker daemon config file which is usually present at /etc/docker/daemon.json:
```bash
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```
[Source](https://github.com/NVIDIA/k8s-device-plugin#preparing-your-gpu-nodes)

## <a id=kubernetes></a> Kubernetes setup

Recommended version is `v1.15.11` for Kubernetes and `v0.7.5` for Kubernetes-CNI.
Please lookup EOL for Kubernetes versions before installing.

```bash
# set environment variables for Kubernetes and CNI
export KUBERNETES_VERSION=1.15.11
export KUBERNETES_CNI=0.7.5

# add kubernetes apt packages
sudo bash -c 'apt-get update && apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF
apt-get -y update'

# install kubernetes packages
sudo apt-get install -yf \
  socat \
  ebtables \
  apt-transport-https \
  kubelet=${KUBERNETES_VERSION}-00 \
  kubeadm=${KUBERNETES_VERSION}-00 \
  kubernetes-cni=${KUBERNETES_CNI}-00 \
  kubectl=${KUBERNETES_VERSION}-00
```

[Source](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)

## <a id=k8s-up></a> Create a single node Kubernetes cluster

A single node Kubernetes cluster does not have ETCD replication or cluster backup. It is not suitable for production workloads.
**Recommended**: HA Kubernetes cluster with cluster backup for production.

### <a id=kubeadm></a> Create cluster with kubeadm
```bash
INGRESS_IP=<UCS machine\'s IP>
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet
sleep 30 # wait for docker, kubelet to restart

sudo swapoff -a
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --apiserver-advertise-address=${INGRESS_IP}
```

### <a id=kubeconfig></a> Copy KUBECONFIG into userspace
```bash
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

export KUBECONFIG=$HOME/.kube/config
```
#### Check KUBECONFIG

`kubectl get nodes -o wide`
```
NAME                   STATUS   ROLES    AGE    VERSION    INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
ucs-kubeflow  Not Ready    master   4d2h   v1.15.11   10.x.x.101   <none>        Ubuntu 18.04.2 LTS   4.15.0-20-generic   docker://18.9.3
```

**Note:** Master node status becomes Ready after Calico is installed in the next steps.

### <a id=add-ons></a> Install cluster add-ons

#### <a id=calico></a> Calico
```bash
kubectl apply -f https://docs.projectcalico.org/v3.11/manifests/calico.yaml
```

##### Taint master node, check calico pods

```bash
# tainting the master node alows pods to be scheduled on it
kubectl taint nodes --all node-role.kubernetes.io/master-
```
Expected output: <br>
`node/ucs-kubeflow untainted`

Ensure the coredns, calico and the kube-proxy pods are running.
```bash
kubectl get pods -n kube-system -w
```
#### <a id=nvidia></a> NVIDIA Device Plugin
The NVIDIA GPU device plugin runs as a Kubernetes daemonset and exposes the underlying GPUs as a usable Kubernetes resource.

```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/master/nvidia-device-plugin.yml
```

#### <a id=rancher></a> Storage Class
The Rancher local-path-provisioner storage class creates host-path mounted persistent-volumes for persistent-volume-claims dynamically. <br>
**Note:**
There are security concerns around host-path volumes as they expose the underlying host filesystem to Kubernetes pods and applications. Container breakouts could be dangerous.

```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml

# set local-path to be default storage class
kubectl patch storageclasses.storage.k8s.io local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

## <a id=k8s-ready></a> Check cluster readiness

Cluster checks:
- [ ] Kubernetes node is ready<br>
    * `kubectl get nodes -o wide`

Expected output:<br>
```
NAME                   STATUS   ROLES    AGE    VERSION    INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
ucs-kubeflow  Ready    master   4d2h   v1.15.11   10.x.x.101   <none>        Ubuntu 18.04.2 LTS   4.15.0-20-generic   docker://18.9.3
```
- [ ] Storage Class is running
    * `kubectl get pods -n local-path-storage`<br>

Expected output:<br>
```
NAME                                      READY   STATUS    RESTARTS   AGE
local-path-provisioner-74c64c9987-vnh76   1/1     Running   0          4d2h
```
- [ ] kube-system pods are running
    * `kubectl get pods -n kube-system`<br>

Expected output:<br>
```
calico-kube-controllers-867fbf6cd4-sxgmw       1/1     Running   0          4d2h
calico-node-762sx                              1/1     Running   0          4d2h
coredns-6dcc67dcbc-8hg5d                       1/1     Running   0          4d2h
coredns-6dcc67dcbc-zj7gn                       1/1     Running   0          4d2h
etcd-ucs-kubeflow                              1/1     Running   0          4d2h
kube-apiserver-ucs-kubeflow                    1/1     Running   0          4d2h
kube-controller-manager-ucs-kubeflow           1/1     Running   0          4d2h
kube-proxy-c8nrt                               1/1     Running   0          4d2h
kube-scheduler-ucs-kubeflow                    1/1     Running   0          4d2h
nvidia-device-plugin-daemonset-xr96d           1/1     Running   0          4d2h
```
