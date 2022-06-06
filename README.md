# XLSX to PDF converter server

## TODO List

- [X] Simplest API
- [ ] Optimize image size
- [X] Migrate on alpine

## What inside?
- Alpine 3.16 (since 0.2.0, Debian bullseye below)
- LibreOffice Calc and LibreOffice Writer
- python 3.10.4
  - fastapi
  - uvicorn

This image based on [python:3.10.4](https://hub.docker.com/_/python).

## Get image
You could pull image from [Docker Hub](https://hub.docker.com/r/holography/xlsx2pdf-libre-api) or build:
```bash
git clone https://github.com/Holography7/xlsx2pdf-libre-api.git
cd xlsx2pdf-libre-api/src
docker build -t xlsx2pdf-libre-api:custom .
```

## Configuration
If you want just to run:
```bash
docker run --env HOST=0.0.0.0 --env PORT=8070 -p 8000:8070 -ti holography/xlsx2pdf-libre-api:0.2.0
```

Or using docker-compose:
```
version: "3.8"

services:
  xlsx2pdf-libre:
    image: holography/xlsx2pdf-libre-api:0.2.0
    network_mode: "host"
    ports:
     - 8000:8070
    environment:
     - HOST=0.0.0.0
     - PORT=8070
```

## Usage
All you need it's just send bytes to API `http://localhost:8000/convert_to_pdf` and it response you PDF bytes.

For example, you could test it by python script `request.py`. Don't forget copy close to it `example.xlsx`.

## Changelog
### 0.2.1
- Improved deletion of temporary files
### 0.2.0
- Migrate on base image python:3.10.4-alpine3.16 (image size decreased ~600MB)
- Now image really using only LibreOffice Calc and LibreOffice Writer (conversion don't work without it)
- Added some debug messages
### 0.1.1
- better handling errors
- added warnings about Java Runtime Environment. I don't know how Libre uses JRM, but in my tests not installed JRM is not critical, so i leave as is.

## This README not ended...
