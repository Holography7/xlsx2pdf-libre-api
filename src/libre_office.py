import logging
import os
import socket
from typing import Optional, List

# you should add /usr/lib/python3/dist-packages/ to Content root to make uno
# and unohelper packages is visible in PyCharm
import uno
import unohelper
# unknown where pyuno grab this modules
from com.sun.star.beans import PropertyValue
from com.sun.star.io import XOutputStream, IOException
from com.sun.star.connection import NoConnectException
from com.sun.star.lang import XComponent

from constants import (
    MARGINS_NAMES,
    DOCUMENT_TITLE,
    SEARCH_FLAGS,
    PRIVATE_STREAM,
    CONVERT_PARAMETER,
)
from settings import DOC_MARGINS, HOST_LIBRE_APP, PORT_LIBRE_APP

logger = logging.getLogger('api')


class Singleton(type):
    """Singleton metaclass"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LibreOffice:
    """Class with base methods for LibreOffice subclasses"""

    def generate_PropertyValue(self, **kwargs) -> List[PropertyValue]:
        """
        Creating of LibreOffice's PropertyValue is very painful, this method
        make this more easily with kwargs: keys = Name, value = Value for
        each PropertyValue object.
        """
        properties = []
        for key, value in kwargs.items():
            prop = PropertyValue()
            prop.Name = key
            prop.Value = value
            properties.append(prop)
        return properties


class OutputStreamWrapper(unohelper.Base, XOutputStream):
    """
    Minimal implementation of XOutputStream. Need to grab bytes of converted
    document. Passed methods used in LibreOffice.
    """
    def __init__(self) -> None:
        self.data = b''
        self.position = 0

    def writeBytes(self, bytes_to_write) -> None:
        self.data += bytes_to_write.value
        self.position += len(bytes_to_write.value)

    def close(self) -> None:
        pass

    def flush(self):
        pass

    def closeOutput(self):
        pass


class LibreOfficeDocument(LibreOffice):
    def __init__(self, document: XComponent):
        self.document = document

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.document.close(True)

    def add_margins(self, margin_mm: int = DOC_MARGINS) -> None:
        sheet_collection = self.document.getSheets()
        count_sheets = sheet_collection.getCount()
        sheets = [sheet_collection.getByIndex(i) for i in range(count_sheets)]
        for sheet in sheets:
            cursor = sheet.createCursor()
            cursor.gotoStartOfUsedArea(False)
            cursor.gotoEndOfUsedArea(True)
            for margin in MARGINS_NAMES:
                cursor.setPropertyValue(margin, margin_mm)
        logger.debug(f'Added margins ({margin_mm} mm).')

    def save(
            self,
            path: Optional[str] = None,
            format_name: str = CONVERT_PARAMETER,
    ) -> Optional[bytes]:
        """
        If set path, this method save document in selected path and returns
        None, otherwise returns bytes of document.
        """
        if path:
            url = uno.systemPathToFileUrl(os.path.abspath(path))
            output_stream = None
            conversion_properties = self.generate_PropertyValue(
                FilterName=format_name,
            )
        else:
            url = PRIVATE_STREAM
            output_stream = OutputStreamWrapper()
            conversion_properties = self.generate_PropertyValue(
                OutputStream=output_stream,
                FilterName='calc_pdf_Export',
            )
        try:
            self.document.storeToURL(url, conversion_properties)
        except IOException as exc:
            raise IOError(exc.Message)
        else:
            logger.debug('Document converted.')
        if output_stream is not None:
            return output_stream.data
        else:
            return None

    def close(self) -> None:
        self.document.close(True)


class LibreOfficeApplication(LibreOffice, metaclass=Singleton):
    """LibreOffice application."""
    def __init__(self) -> None:
        self.__remote_context = None
        self.__service_manager = None
        self.__application = None

    def initialize(self) -> None:
        url = (
            f'uno:socket,host={HOST_LIBRE_APP},port={PORT_LIBRE_APP};urp;'
            f'StarOffice.ComponentContext'
        )
        local_context = uno.getComponentContext()
        resolver = local_context.ServiceManager.createInstanceWithContext(
            'com.sun.star.bridge.UnoUrlResolver',
            local_context,
        )
        try:
            self.__remote_context = resolver.resolve(url)
        except NoConnectException:
            raise IOError(resolver, url)
        else:
            self.__service_manager = self.__remote_context.ServiceManager
            self.__application = \
                self.__service_manager.createInstanceWithContext(
                    'com.sun.star.frame.Desktop',
                    self.__remote_context,
                )
        logger.info('Connection with LibreOffice initialized.')

    def open_document(
            self,
            path: Optional[str] = None,
            file_bytes: Optional[bytes] = None,
    ) -> LibreOfficeDocument:
        """
        Set path argument to read document from filesystem.
        Set file_bytes argument to read document from memory.
        """
        if path and file_bytes:
            raise ValueError(
                'You cannot use both arguments of this method (path, '
                'file_bytes)'
            )
        if path:
            # read from file
            properties = []
            input_stream = None
            url = uno.systemPathToFileUrl(os.path.abspath(path))
        elif file_bytes:
            # read from memory
            url = PRIVATE_STREAM
            input_stream = self.__service_manager.createInstanceWithContext(
                'com.sun.star.io.SequenceInputStream',
                self.__remote_context,
            )
            input_stream.initialize((uno.ByteSequence(file_bytes),))
            properties = self.generate_PropertyValue(
                InputStream=input_stream,
                Hidden=True,
            )
        else:
            raise ValueError('Use path or file_bytes to load document.')
        try:
            document = self.__application.loadComponentFromURL(
                url,
                DOCUMENT_TITLE,
                SEARCH_FLAGS,
                properties,
            )
        except IOException as exc:
            raise IOError(exc.Message)
        else:
            if input_stream is not None:
                input_stream.closeInput()
            logger.debug('Document opened.')
        return LibreOfficeDocument(document)

    def check_application_is_runned(self) -> Optional[bool]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            sock.connect((HOST_LIBRE_APP, PORT_LIBRE_APP))
        except ConnectionRefusedError as exc:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            return False
        else:
            sock.close()
            return True
