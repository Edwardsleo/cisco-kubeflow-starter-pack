#FROM tensorflow/tensorflow:2.3.0-gpu
FROM python:3.6-slim-buster

#RUN apt update && apt install curl unzip wget libsm6 libxext6 libxrender-dev libglib2.0-0 -y
#RUN python3 -m pip install --upgrade pip
#RUN pip install opencv-python==4.1.1.26 lxml tqdm

RUN pip install kubeflow-tfjob kubeflow-fairing kubernetes==10.0.1
COPY src/tfjob-creation.py /opt/tfjob-creation.py
RUN chmod +x /opt/tfjob-creation.py
ENTRYPOINT ["/opt/tfjob-creation.py"]

