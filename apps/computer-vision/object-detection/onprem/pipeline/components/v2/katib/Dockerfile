FROM ubuntu:18.04
RUN apt update
RUN apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    wget

# Install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.19.0/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

# Install Katib, Kubernetes client SDKs & AWSCLI SDK
RUN apt install python3 python3-pip -y
RUN pip3 install kubeflow-katib==0.0.2 kubernetes==10.0.0 awscli==1.18.222

# Install yq tool
RUN wget https://github.com/mikefarah/yq/releases/download/3.3.2/yq_linux_amd64 -O /usr/bin/yq &&\
    chmod +x /usr/bin/yq

ADD src/* /opt/
RUN chmod +x /opt/*

# Modify Kubeflow Katib package
RUN ["/usr/bin/python3", "/opt/hack_katib.py", "/usr/local/lib/python3.6/dist-packages/kubeflow/katib/api_client.py"]
ENTRYPOINT ["/opt/deploy.sh"]
