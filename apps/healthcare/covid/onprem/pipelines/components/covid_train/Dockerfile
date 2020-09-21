FROM python:3.7-slim-buster

RUN pip install tensorflow==1.13.1 --no-cache-dir
RUN pip install keras --no-cache-dir
RUN pip install pandas
ADD ./src/covid-train.py  /opt/covid-train.py
RUN chmod +x /opt/*
ENTRYPOINT ["/usr/local/bin/python3"]
CMD ["/opt/covid-train.py"]
