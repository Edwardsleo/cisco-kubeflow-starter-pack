# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM tensorflow/tensorflow:2.3.0-gpu
RUN apt update
RUN apt install -y wget git libgtk2.0-dev vim

ENV APP_HOME /app

RUN mkdir -p $APP_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY model.py  $APP_HOME

WORKDIR $APP_HOME
CMD ["python", "model.py"]
