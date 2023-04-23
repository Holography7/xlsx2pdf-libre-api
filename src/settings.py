import os

HOST, PORT = os.environ.get('HOST', 'localhost:8070').split(':')
PORT = int(PORT)
HOST_LIBRE_APP, PORT_LIBRE_APP = os.environ.get(
    'HOST_LIBRE_APP',
    'localhost:2002',
).split(':')
PORT_LIBRE_APP = int(PORT_LIBRE_APP)
DOC_MARGINS = int(os.environ.get('MARGIN', 99))
