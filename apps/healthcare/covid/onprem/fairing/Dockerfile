FROM python:3.7-slim-buster

RUN pip install tensorflow==1.13.1 --no-cache-dir
RUN pip install keras --no-cache-dir
RUN pip install pandas
ADD covid-model.py  /opt/covid-model.py
ADD train.csv /opt/train.csv
ADD test.csv /opt/test.csv
RUN chmod +x /opt/*
ENTRYPOINT ["/usr/local/bin/python3"]
CMD ["/opt/covid-model.py"]
