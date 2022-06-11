import tempfile
import os
from logging.config import dictConfig
import logging
import argparse

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

from constants import CONVERT_PARAMETER, RUN_ARGUMENTS
from logger import LogConfig
from libre_office import LibreOfficeApplication


dictConfig(LogConfig().dict())
logger = logging.getLogger('api')
app = FastAPI()


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
        tmp_file_pdf = f'{temp_xlsx_file.name}.pdf'
        temp_xlsx_file.write(data)
        try:
            document = libre_office.open_document(temp_xlsx_file.name)
            if margin:
                document.add_margins(99)
            document.save(tmp_file_pdf, CONVERT_PARAMETER)
            document.close()
        except IOError as exc:
            logger.error(exc)
            raise HTTPException(exc)
    with open(tmp_file_pdf, 'rb') as temp_pdf_file:
        pdf = temp_pdf_file.read()
    os.remove(tmp_file_pdf)
    logger.debug('Sending PDF back.')
    return Response(
        content=pdf,
        media_type='application/octet-stream',
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg, params in RUN_ARGUMENTS.items():
        parser.add_argument(arg, **params)
    args = parser.parse_args()
    host, port = args.host.split(':') if ':' in args.host else (args.host, 80)
    if isinstance(port, str):
        port = int(port)
    margin = args.add_margins if args.add_margins else 0
    try:
        libre_office = LibreOfficeApplication('localhost', 2002)
    except IOError as libre_exc:
        raise RuntimeError(f'Failed to connect with LibreOffice: {libre_exc}')
    else:
        uvicorn.run(app, host=host, port=port)
