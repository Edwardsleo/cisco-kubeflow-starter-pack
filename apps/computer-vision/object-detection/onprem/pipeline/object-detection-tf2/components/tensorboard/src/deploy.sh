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
       esac
done

cd ${NFS_PATH}

export NFS_PATH=${NFS_PATH}/${TIMESTAMP}

echo $NFS_PATH

touch object-detection-tensorboard-$TIMESTAMP.yaml

cat >> object-detection-tensorboard-$TIMESTAMP.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: object-detection-deployment-${TIMESTAMP}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: object-detection-deployment-${TIMESTAMP}
  template:
    metadata:
      annotations:
        sidecar.istio.io/inject: "false"
      labels:
        app: object-detection-deployment-${TIMESTAMP}
    spec:
      containers:
      - name: object-detection-deployment-${TIMESTAMP}
        image: tensorflow/tensorflow:1.15.2-py3
        imagePullPolicy: Always
        command:
        - /usr/local/bin/tensorboard
        - --logdir=$NFS_PATH
        - --port=80
        ports:
        - name: http
          containerPort: 80
          protocol: TCP
        resources:
          requests:
            cpu: "2"
            memory: "2Gi"
        volumeMounts:
        - mountPath: "/mnt/"
          name: "nfsvolume"
      volumes:
       - name: "nfsvolume"
         persistentVolumeClaim:
           claimName: "nfs"
---
apiVersion: v1
kind: Service
metadata:
  name: object-detection-service-${TIMESTAMP}
spec:
  ports:
    - port: 80
      protocol: TCP
      name: http
  selector:
    app: object-detection-deployment-${TIMESTAMP}
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: object-detection-virtualsvc-${TIMESTAMP}
spec:
  gateways:
  - kubeflow/kubeflow-gateway
  hosts:
  - '*'
  http:
  - match:
    - uri:
        prefix: /${TIMESTAMP}/tensorboard/
    rewrite:
      uri: /
    route:
    - destination:
        host: object-detection-service-${TIMESTAMP}.kubeflow.svc.cluster.local
        port:
          number: 80
---

EOF

# Creating katib experiment

kubectl apply -f object-detection-tensorboard-$TIMESTAMP.yaml -n kubeflow

sleep 5
