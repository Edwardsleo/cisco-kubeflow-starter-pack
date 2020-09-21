FROM tensorflow/tensorflow:1.15.2-py3
RUN pip install pandas dill alibi==0.3.2
ADD blerssi-model.py  /opt/blerssi-model.py
ADD iBeacon_RSSI_Labeled.csv /opt/iBeacon_RSSI_Labeled.csv
RUN chmod +x /opt/blerssi-model.py  /opt/iBeacon_RSSI_Labeled.csv 
CMD ["python","/opt/blerssi-model.py"]
