FROM python:3.10-slim-buster

RUN apt-get update && \
    apt-get -y install gcc build-essential  && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt
