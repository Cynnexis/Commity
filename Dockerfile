# cynnexis/commity
#
# To build this image:
# docker build -t cynnexis/commity .

FROM python:3.7.6-buster

USER root
WORKDIR /root/commity

COPY . .
RUN chmod +x docker-script.sh
RUN chmod +x install-default-environment.sh
RUN ./install-default-environment.sh

ENTRYPOINT ["bash", "./docker-script.sh"]
