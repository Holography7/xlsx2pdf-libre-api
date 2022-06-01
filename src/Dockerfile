FROM python:3.10.4

WORKDIR /usr/src/api

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y libreoffice --no-install-recommends fonts-liberation2 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install fastapi "uvicorn[standard]"

COPY ./docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

COPY ./logger.py .
COPY ./api.py .

ENTRYPOINT ./docker-entrypoint.sh
