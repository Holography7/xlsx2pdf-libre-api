import time

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response
from fastapi_health import health

from libre_office import LibreOfficeApplication
from settings import HOST, PORT, DOC_MARGINS
from logger import logger

app = FastAPI()
libre_office = LibreOfficeApplication()


def is_connected_with_libre_office(
        is_connected: bool = Depends(libre_office.check_application_is_runned),
):
    message = {'connect_with_libre_office': 'OK' if is_connected else 'Failed'}
    if is_connected:
        logger.debug(message)
    else:
        logger.error(message)
    return message


app.add_api_route(
    '/health',
    health([is_connected_with_libre_office]),
    methods=['GET', 'HEAD']
)


@app.post(
    '/convert_to_pdf',
    responses={200: {'content': {'application/octet-stream': {}}}},
    response_class=Response,
)
async def convert_to_pdf(request: Request) -> Response:
    logger.debug('Request accepted.')
    data: bytes = await request.body()
    logger.debug('Document saved in memory.')
    try:
        with libre_office.open_document(file_bytes=data) as document:
            if DOC_MARGINS:
                document.add_margins()
            pdf = document.save()
    except IOError as exc:
        logger.error(exc)
        raise HTTPException(exc)
    return Response(
        content=pdf,
        media_type='application/octet-stream',
    )

if __name__ == '__main__':
    for i in range(10):
        try:
            libre_office.check_application_is_runned()
        except ConnectionRefusedError:
            logger.info(f'Waiting start LibreOffice (tried {i + 1} of 10)...')
            time.sleep(3)
        else:
            try:
                libre_office.initialize()
            except IOError as libre_exc:
                raise RuntimeError(
                    f'Failed to connect with LibreOffice: {libre_exc}'
                )
            else:
                break
    uvicorn.run(app, host=HOST, port=PORT)
