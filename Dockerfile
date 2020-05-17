# cynnexis/commity
#
# To build this image:
# docker build -t cynnexis/commity .

FROM python:3.7.6-buster

USER root
ENV DEBIAN_FRONTEND noninteractive
WORKDIR /root/commity

RUN apt-get update -y && \
	apt-get install -y \
		dos2unix \
		make

COPY . .

# Some files on Windows use CRLF newlines. It is incompatible with UNIX.
RUN dos2unix *.sh && chmod +x *.sh

# Install environment
RUN ./install-default-environment.sh

ENTRYPOINT ["bash", "./docker-entrypoint.sh"]
