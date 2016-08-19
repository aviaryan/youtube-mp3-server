FROM python:2-alpine
MAINTAINER Avi Aryan <avi.aryan123@gmail.com>

ENV INSTALL_PATH /ymp3
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY . .

# install deps
RUN apk update
RUN apk add --no-cache --virtual build-dependencies gcc python-dev libevent-dev linux-headers musl-dev postgresql postgresql-dev\
	&& pip install -r requirements.txt \
	&& apk del build-dependencies

# update tar .. --strip-componenets not available in current version
# install ffmpeg
# wget, tar etc already present
RUN apk --update add --no-cache tar xz
RUN ash scripts/set_ffmpeg.sh

# update needed for wget
RUN apk --update add --no-cache ca-certificates wget
RUN update-ca-certificates

CMD python app.py
