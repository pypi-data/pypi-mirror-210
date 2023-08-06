FROM python:3.10-slim-bullseye

RUN apt-get update
RUN apt-get install -y procps
RUN apt-get install -y curl

RUN mkdir /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

RUN rm -r /usr/src/app