FROM housebw/darknet:latest
RUN apt update

ADD src/deploy.sh /opt
RUN chmod +x /opt/deploy.sh
ENTRYPOINT ["/opt/deploy.sh"]
