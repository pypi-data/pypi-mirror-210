"""Copyright © 2023 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from oathlink.util.https.https import _post

def reportRecord(certificateFilename: str, keyFilename: str, recordId: [str, list]) -> list:
    extension = 'report/record'
    recordId = _recordIdToList(recordId=recordId)
    payload = {'uuid': recordId}
    response = _post(certificateFilename=certificateFilename, keyFilename=keyFilename, extension=extension,
                     payload=payload)
    return response

def _recordIdToList(recordId: [str, list]) -> list:
    if recordId is None:
        recordId = []
    if isinstance(recordId, str):
        recordId = [recordId]
    return recordId