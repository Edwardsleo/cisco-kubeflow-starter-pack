# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim
RUN apt update
RUN apt install -y libgtk2.0-dev
RUN apt install git -y
RUN python -m pip install --upgrade pip
RUN pip install awscli tensorflow==1.15.0 pillow

# Install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.19.0/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh

ENTRYPOINT ["/opt/deploy.sh"]
