FROM tensorflow/tensorflow:2.3.0-gpu
RUN apt update && apt install curl unzip wget libsm6 libxext6 libxrender-dev libglib2.0-0 libgl1-mesa-glx -y
RUN python3 -m pip install --upgrade pip
RUN pip install opencv-python==4.1.1.26 lxml tqdm PyQt5
COPY src/yolov3-tf2/ /opt/yolov3-tf2
ADD src/main.sh /opt/
RUN chmod +x /opt/main.sh
ENTRYPOINT ["/opt/main.sh"]

