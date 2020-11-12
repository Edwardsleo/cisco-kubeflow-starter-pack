FROM python:3.6-slim-buster
RUN pip install kubeflow-tfjob kubeflow-fairing kubernetes==10.0.1
COPY src/tfjob-creation.py /opt/tfjob-creation.py
RUN chmod +x /opt/tfjob-creation.py
ENTRYPOINT ["/opt/tfjob-creation.py"]

