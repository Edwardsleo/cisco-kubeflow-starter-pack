FROM tensorflow/tensorflow:2.3.0
RUN apt update && apt install libsm6 libxext6 libxrender-dev libglib2.0-0 -y
RUN python3 -m pip install --upgrade pip
RUN pip install awscli opencv-python==4.1.1.26 tf-nightly==2.4.0.dev20200902
COPY /src/yolov3-tf2/ /opt/yolov3-tf2
ADD src/main.sh /opt/
RUN chmod +x /opt/main.sh
ENTRYPOINT ["/opt/main.sh"]
