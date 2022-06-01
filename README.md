# XLSX to PDF converter server

## TODO List

- [X] Simplest API
- [ ] Optimize image size
- [ ] Migrate on alpine

## What inside?
- Debian bullseye
- LibreOffice Calc without most GUI packages
- python 3.10.4
  - fastapi
  - uvicorn

This image based on [python:3.10.4](https://hub.docker.com/_/python).

Source code of API maybe coming up on GitHub soon.

## Get image
You could pull image from [Docker Hub](https://hub.docker.com/r/holography/xlsx2pdf-libre-api) or build:
```bash
wget
docker build -t xlsx2pdf-libre-api:custom .
```

## Configuration
If you want just to run:
```bash
docker run --env HOST=0.0.0.0 --env PORT=8070 -p 8000:8070 -ti holography/xlsx2pdf-libre-api:0.1.1
```

Or using docker-compose:
```
version: "3.8"

services:
  xlsx2pdf-libre:
    image: holography/xlsx2pdf-libre-api:0.1.1
    network_mode: "host"
    ports:
     - 8000:8070
    environment:
     - HOST=0.0.0.0
     - PORT=8070
```

## Usage
All you need it's just send bytes to API `http://localhost:8070/convert_to_pdf` and it response you PDF bytes.

For example, you could test it by python script `request.py`. Don't forget copy close to it `example.xlsx`.

## Changelog
### 0.1.1
- better handling errors
- added warnings about Java Runtime Environment. I don't know how Libre uses JRM, but in my tests not installed JRM is not critical, so i leave as is.

## This README not ended...
