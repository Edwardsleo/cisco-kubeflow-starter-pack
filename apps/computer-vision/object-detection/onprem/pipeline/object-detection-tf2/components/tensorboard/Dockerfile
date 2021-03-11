FROM ubuntu:18.04
RUN apt update
RUN apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

# Install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.19.0/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh
ENTRYPOINT ["/opt/deploy.sh"]
