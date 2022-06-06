import tempfile
import subprocess
import os
from logging.config import dictConfig
import logging
from sys import argv

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

from logger import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger('api')
app = FastAPI()
JAVA_WARNING = (
    'javaldx: Could not find a Java Runtime Environment!\n'
    'Please ensure that a JVM and the package libreoffice-java-common\n'
    'is installed.\n'
    'If it is already installed then try removing ~/.config/libreoffice/4/user'
    '/config/javasettings_Linux_*.xml\n'
    'Warning: failed to read path from javaldx\n'
)
JAVA_SHORT_WARNING = (
    'javaldx: Could not find a Java Runtime Environment!\n'
    'Warning: failed to read path from javaldx\n'
)


@app.post(
    '/convert_to_pdf',
    responses={200: {'content': {'application/octet-stream': {}}}},
    response_class=Response,
)
async def convert_to_pdf(request: Request) -> Response:
    logger.debug('Accepting bytes...')
    data: bytes = await request.body()
    logger.debug('Converting...')
    with tempfile.NamedTemporaryFile() as temp_xlsx_file:
        temp_xlsx_file.write(data)
        output = subprocess.run([
            'libreoffice',
            '--calc',
            '--headless',
            '--convert-to',
            'pdf',
            temp_xlsx_file.name,
            '--outdir',
            '/tmp',
        ], capture_output=True)
        logger.debug('Conversion ended. Watching stdout and stderr...')
        err = output.stderr.decode('utf-8')
        if JAVA_WARNING in err:
            for msg in JAVA_WARNING[:-1].split('\n'):
                logger.warning(msg)
            err = err.replace(JAVA_WARNING, '')
        if JAVA_SHORT_WARNING in err:
            for msg in JAVA_SHORT_WARNING[:-1].split('\n'):
                logger.warning(msg)
            err = err.replace(JAVA_SHORT_WARNING, '')
        if err:
            logger.error(err[:-1])
            raise HTTPException(status_code=500, detail=err)
        else:
            logger.info(output.stdout.decode('utf-8')[:-1])
            tmp_file = f'{temp_xlsx_file.name}.pdf'
    with open(tmp_file, 'rb') as temp_pdf_file:
        pdf = temp_pdf_file.read()
    os.remove(tmp_file)
    logger.debug('Sending PDF back.')
    return Response(
        content=pdf,
        media_type='application/octet-stream',
    )

if __name__ == '__main__':
    if len(argv) == 1:
        logger.error('HOST and PORT not defined!')
    elif len(argv) == 2 and not argv[1].isdigit():
        logger.error('PORT not defined!')
    elif len(argv) == 2 and argv[1].isdigit():
        logger.error('HOST not defined!')
    else:
        host = argv[1]
        port = int(argv[2])
        uvicorn.run(app, host=host, port=port)
