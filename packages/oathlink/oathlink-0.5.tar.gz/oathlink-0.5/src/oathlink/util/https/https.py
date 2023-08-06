"""Copyright © 2023 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
import requests

def _getBaseUrl() -> str:
    return 'https://api.oathlink.com'

def _getUrl(extension: str) -> str:
    if len(extension) > 0:
        if extension[0] == '/':
            extension = extension[1:]
    return f'{_getBaseUrl()}/{extension}'

def get(url: str, filename: str) -> str:
    response = requests.get(url)
    if filename == '':
        return response.text
    with open(filename, 'rb') as file:
        file.write(response.content)
    return filename

def put(url: str, filename: str) -> bool:
    response = requests.put(url, data=open(filename, 'rb')).text
    print(response)
    return True

def _post(certificateFilename: str, keyFilename: str, extension: str = None, payload: dict = None):
    if extension is None:
        extension = ''
    if payload is None:
        payload = {}
    cert = (certificateFilename, keyFilename)
    data = json.dumps(payload)
    response = requests.post(_getUrl(extension), data=data, cert=cert)
    return response.text

def _get(certificateFilename: str, keyFilename: str, extension: str = None):
    if extension is None:
        extension = ''
    cert = (certificateFilename, keyFilename)
    response = requests.get(_getUrl(extension), cert=cert)
    return response.text