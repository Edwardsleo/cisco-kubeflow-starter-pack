# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim
RUN apt update
RUN apt install -y libgtk2.0-dev
RUN pip install awscli
RUN apt install git -y

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh

ENTRYPOINT ["/opt/deploy.sh"]
