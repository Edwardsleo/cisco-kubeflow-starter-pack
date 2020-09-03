# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim
RUN apt update
RUN apt install -y wget git curl zip unzip
RUN pip install awscli

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh

ENTRYPOINT ["/opt/deploy.sh"]
