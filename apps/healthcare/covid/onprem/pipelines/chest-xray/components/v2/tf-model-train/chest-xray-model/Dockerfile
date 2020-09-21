FROM tensorflow/tensorflow:1.15.2-gpu
RUN apt-get update -y
RUN apt-get install -y libsm6 libxext6 libxrender-dev 
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y wget
RUN pip install -U scikit-learn
RUN pip install kubernetes==10.0.1 kubeflow-fairing==0.7.2  --no-cache-dir
RUN pip install minio==5.0.10 --no-cache-dir
RUN pip install pandas opencv-python==4.3.0.36 pydicom pillow imutils xlsxwriter matplotlib dill
ADD src/covid-xray-model.py  /opt/covid-xray-model.py
ADD src/data/datasets /opt/data/datasets
RUN chmod +x /opt/covid-xray-model.py  /opt/data/datasets
WORKDIR /opt/
CMD python covid-xray-model.py
