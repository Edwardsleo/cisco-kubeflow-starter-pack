FROM tensorflow/tensorflow:1.7.0-py3
RUN pip install kubeflow-katib==0.0.2 kubernetes==10.0.1 dill
ADD chest-xray-katib.py  /opt/chest-xray-katib.py
RUN chmod 755 /opt/chest-xray-katib.py 
ENTRYPOINT ["/usr/bin/python"]
CMD ["/opt/chest-xray-katib.py"]

