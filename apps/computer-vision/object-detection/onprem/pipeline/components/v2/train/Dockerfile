FROM daisukekobayashi/darknet:gpu-cv-cc75
RUN apt update
RUN apt install curl python3 python3-pip bsdmainutils -y

# Install awscli
RUN pip3 install awscli

# Install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.19.0/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh
ENTRYPOINT ["/opt/deploy.sh"]
