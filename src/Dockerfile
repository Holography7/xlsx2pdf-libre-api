FROM python:3.10.4

WORKDIR /usr/src/api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:/usr/lib/python3/dist-packages/
ENV MARGIN 0

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y libreoffice-calc --no-install-recommends fonts-liberation2 libreoffice-script-provider-python python3-uno supervisor && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./logger.py .
COPY ./constants.py .
COPY ./libre_office.py .
COPY ./api.py .

COPY ./supervisord.conf .

CMD ["supervisord", "-c", "/usr/src/api/supervisord.conf"]
