FROM python:3.10.4-alpine3.16

WORKDIR /usr/src/api

RUN apk add --no-cache build-base ttf-liberation
RUN fc-cache -fv
RUN apk add --no-cache libreoffice-calc libreoffice-writer
RUN pip install --upgrade pip
RUN pip install fastapi "uvicorn[standard]"

COPY ./docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

COPY ./logger.py .
COPY ./api.py .

ENTRYPOINT ./docker-entrypoint.sh
