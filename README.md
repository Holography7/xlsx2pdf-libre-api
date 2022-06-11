# XLSX to PDF converter server

## TODO List

- [X] Simplest API
- [ ] Optimize image size
- [ ] Migrate on alpine

## What inside?
- Debian bullseye (Alpine 3.16 in versions 0.2.x)
- LibreOffice Calc
- python 3.10.4
  - fastapi
  - uvicorn
  - pyuno (a.k.a UNO for LibreOffice)

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
docker run --env HOST=0.0.0.0:8070 -p 8000:8070 -ti holography/xlsx2pdf-libre-api:0.3.0
```

Or using `docker-compose`:
```
version: "3.7"

services:
  xlsx2pdf-libre:
    image: holography/xlsx2pdf-libre-api:0.3.0
    ports:
     - 8000:8070
    environment:
     - HOST=0.0.0.0:8070
```

Or, if you downloaded sources:
```bash
cd ../deploy
docker-compose up
```
You can add `-d` parameter to `docker-compose up` if you don't want lock your terminal.

### NEW in 0.3.0
For unknown reasons in LibreOffice inner cell margins less than in MS Excel. If you need them, add `--env MARGIN=99` to `docker run` command, or ` - MARGIN=99` in `environment` section of docker-compose file.

## Usage
All you need it's just send bytes to API `http://localhost:8000/convert_to_pdf` and it responds you PDF bytes.

For example, you could test it by python script `request.py`. Don't forget copy close to it `example.xlsx`.

## Changelog
### 0.3.0
- Unfortunately, this changes forced return to Debian image:
  - Added ability to increase inner cell margins to do PDF file more like from MS Excel.
  - Optimized conversion.
- Now not needed to select HOST and PORT by different environments. Use HOST=0.0.0.0:8070 instead, or don't specify port and then API will run with port 80 automatically.
- LibreOffice now will stay run all lifetime of container. If it crushed, supervisord should restart it automatically.
- Java warnings not send by API anymore, they send by LibreOffice.
### 0.2.1
- Improved deletion of temporary files
### 0.2.0
- Migrate on base image python:3.10.4-alpine3.16 (image size decreased ~600MB).
- Now image really using only LibreOffice Calc and LibreOffice Writer (conversion don't work without it).
- Added some debug messages.
### 0.1.1
- better handling errors.
- added warnings about Java Runtime Environment. I don't know how Libre uses JRM, but in my tests not installed JRM is not critical, so I leave as is.

## This README not ended...
