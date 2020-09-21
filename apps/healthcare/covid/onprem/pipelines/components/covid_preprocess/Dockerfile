FROM python:3.7-slim-buster

RUN pip install pandas --no-cache-dir
ADD ./src/covid-preprocess.py  /opt/covid-preprocess.py
ADD ./src/data/train.csv /opt/train.csv
ADD ./src/data/test.csv /opt/test.csv
RUN chmod +x /opt/* 
ENTRYPOINT ["/usr/local/bin/python3"]
CMD ["/opt/covid-preprocess.py"]
