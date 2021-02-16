FROM ubuntu:16.04
RUN apt update && apt install -y python3 python3-pip dos2unix
RUN apt install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev \
libavformat-dev libswscale-dev libopencv-dev python-dev python-numpy libtbb2 libtbb-dev \
libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev unzip
RUN apt install -y wget gcc g++ make cmake 
RUN pip3 install awscli==1.18.222
RUN cd \
    && wget https://github.com/opencv/opencv/archive/4.0.1.zip \
    && unzip 4.0.1.zip \
    && cd opencv-4.0.1 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j8 \
    && make install \
    && cd \
    && rm 4.0.1.zip
RUN git clone https://github.com/xiangweizeng/darknet2ncnn.git \ 
    && cd darknet2ncnn \
    && git submodule init \ 
    && git submodule update
ADD src/deploy.sh /opt
ADD src/scripts /opt/scripts
RUN chmod +x /opt/deploy.sh
RUN chmod +x /opt/scripts/patchParam.py
ENTRYPOINT ["/opt/"]
