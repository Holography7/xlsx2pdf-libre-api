import tempfile
import subprocess
import os
from logging.config import dictConfig
import logging
from sys import argv

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse

from logger import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger('api')
app = FastAPI()
tmp_file = ''
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


def clear_temp_file() -> None:
    global tmp_file
    if tmp_file:
        os.remove(tmp_file)


@app.post('/convert_to_pdf')
async def convert_to_pdf(request: Request) -> FileResponse:
    logger.debug('Accepting bytes...')
    global tmp_file
    clear_temp_file()
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
    logger.debug('Sending PDF back.')
    return FileResponse(
        path=tmp_file,
        filename=tmp_file[5:],
        media_type='application/pdf',
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
        clear_temp_file()
