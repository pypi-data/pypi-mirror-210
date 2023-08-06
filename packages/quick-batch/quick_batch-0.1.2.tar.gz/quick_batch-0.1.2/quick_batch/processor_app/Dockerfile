FROM python:3.10-slim-bullseye

RUN apt-get update

RUN mkdir /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

COPY processor_requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/processor_requirements.txt

RUN rm -r /usr/src/app