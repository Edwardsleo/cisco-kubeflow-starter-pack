FROM python:3.7-slim-buster
RUN pip install kubernetes==10.0.1 kubeflow-fairing  --no-cache-dir
RUN pip install minio --no-cache-dir
ADD ./src/download-dataset.py  /opt/download-dataset.py
RUN chmod +x /opt/download-dataset.py
ENTRYPOINT ["/usr/local/bin/python3"]
CMD ["/opt/download-dataset.py"]
