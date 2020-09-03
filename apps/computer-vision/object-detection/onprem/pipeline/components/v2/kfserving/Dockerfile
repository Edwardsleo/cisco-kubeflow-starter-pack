FROM python:3.7-slim
RUN apt update
RUN pip install kubernetes==10.0.1 kfserving==0.3.0

ADD src/kfservingdeployer.py /opt

ENTRYPOINT ["/opt/kfservingdeployer.py"]
