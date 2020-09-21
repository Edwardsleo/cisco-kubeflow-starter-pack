FROM tensorflow/tensorflow:1.15.2-gpu
RUN apt-get update -y
RUN apt-get install -y libsm6 libxext6 libxrender-dev 
RUN apt-get install -y wget
RUN pip install -U scikit-learn
RUN pip install kubernetes==10.0.1 kubeflow-fairing  --no-cache-dir
RUN pip install minio --no-cache-dir
RUN pip install pandas opencv-python pydicom pillow imutils xlsxwriter matplotlib dill
ADD src/covid-xray-katib.py  /opt/covid-xray-katib.py
RUN chmod +x /opt/covid-xray-katib.py
WORKDIR /opt/
CMD python covid-xray-katib.py
