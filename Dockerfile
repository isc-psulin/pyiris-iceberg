ARG IMAGE=intersystemsdc/iris-community:2024.2-zpm
FROM $IMAGE

WORKDIR /home/irisowner/dev

RUN mkdir -p /tmp/iceberg

ARG TESTS=0
ARG MODULE="pyiris-iceberg"
ARG NAMESPACE="USER"

## Embedded Python environment
ENV IRISNAMESPACE "IRISAPP" 

ENV PYTHON_PATH=/usr/irissys/bin/
ENV PATH "/usr/irissys/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/irisowner/bin:/home/irisowner/.local/bin"
ENV IRISICE_CONFIG_PATH "local_testing_config.json"

# SQLite
USER root

RUN apt-get update 
RUN apt-get install -y sqlite3 libsqlite3-dev


USER 51773 

## Start IRIS
RUN --mount=type=bind,src=.,dst=. \
    #python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt && \
    iris start IRIS && \
    iris merge IRIS merge.cpf && \
    irispython iris_script.py && \
    iris stop IRIS quietly
