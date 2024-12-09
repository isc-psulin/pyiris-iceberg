ARG IMAGE=intersystemsdc/iris-community:2024.2-zpm
FROM $IMAGE

WORKDIR /home/irisowner/dev

ARG TESTS=0
ARG MODULE="iris-iceberg"
ARG NAMESPACE="USER"


# create Python env
## Embedded Python environment
## Changed^ namespace
ENV IRISNAMESPACE "IRISAPP"
ENV PYTHON_PATH=/usr/irissys/bin/
ENV PATH "/usr/irissys/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/irisowner/bin:/home/irisowner/.local/bin"

# SQLite
USER root

RUN apt-get update
# RUN apt-get update && apt-get -y upgrade \ 
#  && apt-get -y install unattended-upgrades

RUN apt-get install -y sqlite3 libsqlite3-dev
 
USER 51773 

## Start IRIS
RUN --mount=type=bind,src=.,dst=. \
#    pip install --upgrade pip   \
    pip3 install -r requirements-docker.txt && \
    iris start IRIS && \
    iris merge IRIS merge.cpf && \
    irispython iris_script.py

RUN sleep 3

RUN iris stop IRIS quietly