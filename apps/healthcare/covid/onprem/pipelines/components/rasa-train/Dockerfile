FROM ubuntu:18.04

RUN apt-get update -y && apt-get install --no-install-recommends -y -q \
     ca-certificates python3-dev python3-pip python3-setuptools python3-wheel wget \
        build-essential libssl-dev libffi-dev

RUN python3 -m pip install --upgrade pip
RUN pip3 install rasa tornado

ADD rasa/ /ml

ADD ./src/deploy.sh /bin/.
RUN chmod +x /bin/deploy.sh

ENTRYPOINT ["/bin/deploy.sh"]
