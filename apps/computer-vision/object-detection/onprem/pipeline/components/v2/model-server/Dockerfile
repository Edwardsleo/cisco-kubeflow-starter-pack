# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim
RUN apt update
RUN apt install -y wget git libgtk2.0-dev vim

ENV APP_HOME /app
#ENV REPO_NAME tensorflow-yolo

RUN mkdir -p $APP_HOME
# Install production dependencies.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

# Download repo
#RUN git clone https://github.com/hunglc007/tensorflow-yolov4-tflite.git $APP_HOME/$REPO_NAME

# Copy local code to container image
COPY model.py  $APP_HOME
#COPY model.py  $APP_HOME/$REPO_NAME/

#WORKDIR $APP_HOME/$REPO_NAME
WORKDIR $APP_HOME
CMD ["python", "model.py"]
