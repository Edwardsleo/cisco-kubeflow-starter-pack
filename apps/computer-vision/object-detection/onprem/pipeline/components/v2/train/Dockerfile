FROM daisukekobayashi/darknet:gpu-cv-cc75
RUN apt update
RUN apt install curl -y

# Install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.19.0/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh
ENTRYPOINT ["/opt/deploy.sh"]
