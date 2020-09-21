FROM tensorflow/tensorflow:1.7.0-py3
RUN pip install kubeflow-katib kubernetes==10.0.1
ADD blerssi-katib.py  /opt/blerssi-katib.py
RUN chmod +x /opt/blerssi-katib.py 
ENTRYPOINT ["/usr/bin/python"]
CMD ["/opt/blerssi-katib.py"]

