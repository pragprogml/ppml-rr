FROM apache/airflow:2.5.2-python3.10

USER root

RUN apt-get update && \
    apt-get -y install gcc build-essential docker.io procps iputils-ping  && \
    rm -rf /var/lib/apt/lists/*

RUN adduser airflow docker

USER airflow
COPY docker/airflow/requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

# FIXME: Check
# RUN mkdir -p /opt/airflow/log_appender
# COPY docker/airflow/config/log/stdout.py /opt/airflow/log_appender/stdout.py
