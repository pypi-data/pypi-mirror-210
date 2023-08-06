FROM python:3.10-slim-bullseye

RUN apt-get update
RUN apt-get install -y procps
RUN apt-get install -y apt-utils
RUN apt-get update
RUN apt-get install -y curl 
RUN apt-get install -y zip
RUN apt-get install -y unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN apt-get update
RUN rm awscliv2.zip
RUN rm -r aws


RUN mkdir /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

COPY processor_requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/processor_requirements.txt

RUN rm -r /usr/src/app