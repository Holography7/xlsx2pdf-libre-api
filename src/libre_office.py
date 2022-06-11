import os
from typing import Union

import uno

from constants import MARGINS_NAMES

NoConnectException = uno.getClass('com.sun.star.connection.NoConnectException')
IOException = uno.getClass('com.sun.star.io.IOException')
DocumentClass = uno.getClass('com.sun.star.lang.XComponent')


class LibreOfficeDocument:
    def __init__(self, document: DocumentClass):
        self.document = document

    def add_margins(self, margin_mm: int) -> None:
        sheet_collection = self.document.getSheets()
        count_sheets = sheet_collection.getCount()
        sheets = [sheet_collection.getByIndex(i) for i in range(count_sheets)]
        for sheet in sheets:
            cursor = sheet.createCursor()
            cursor.gotoStartOfUsedArea(False)
            cursor.gotoEndOfUsedArea(True)
            for margin in MARGINS_NAMES:
                cursor.setPropertyValue(margin, margin_mm)

    def save(self, path, format_name) -> None:
        url = uno.systemPathToFileUrl(os.path.abspath(path))
        format_filter = uno.createUnoStruct('com.sun.star.beans.PropertyValue')
        format_filter.Name = 'FilterName'
        format_filter.Value = format_name
        try:
            self.document.storeToURL(url, (format_filter,))
        except IOException as exc:
            raise IOError(exc.Message)

    def close(self) -> None:
        self.document.close(True)


class LibreOfficeApplication:
    def __init__(self, host_app: str, port_app: Union[int, str]) -> None:
        url = (
            f'uno:socket,host={host_app},port={port_app};urp;StarOffice.'
            f'ComponentContext'
        )
        local_context = uno.getComponentContext()
        resolver = local_context.ServiceManager.createInstanceWithContext(
            'com.sun.star.bridge.UnoUrlResolver',
            local_context,
        )
        try:
            remote_context = resolver.resolve(url)
        except NoConnectException:
            raise IOError(resolver, url)
        else:
            service_manager = remote_context.ServiceManager
            self.application = service_manager.createInstanceWithContext(
                'com.sun.star.frame.Desktop',
                remote_context,
            )

    def open_document(self, path: str) -> LibreOfficeDocument:
        url = uno.systemPathToFileUrl(os.path.abspath(path))
        try:
            return LibreOfficeDocument(
                self.application.loadComponentFromURL(url, '_blank', 0, ()),
            )
        except IOException as exc:
            raise IOError(exc.Message)
