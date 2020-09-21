FROM tensorflow/tensorflow:1.14.0-py3
RUN pip install -U scikit-learn
RUN pip install keras pandas imblearn matplotlib xlsxwriter
ADD src/network_model.py  /opt/network_model.py
ADD src/Network_Traffic.csv /opt/Network_Traffic.csv
RUN chmod +x /opt/network_model.py  /opt/Network_Traffic.csv
WORKDIR /opt/
RUN mkdir -p /mnt/Model_Network
CMD python network_model.py
