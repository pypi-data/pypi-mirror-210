"""Copyright © 2023 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from oathlink.services.hello import helloOathlink
from oathlink.services.record.upload import getOathlinkUpload
from oathlink.services.record.download import getOathlinkDownload
from oathlink.services.record.decrypt import decryptOathId
from oathlink.services.record.archive import archiveOathlink
from oathlink.services.record.cancel import cancelOathlink
from oathlink.services.agent.account.create import createAgent
from oathlink.services.agent.ip.add import addIP
from oathlink.services.agent.ip.remove import removeIP
from oathlink.services.agent.account.link import linkAgents
from oathlink.services.agent.account.unlink import unlinkAgents
from oathlink.services.report.outstanding import reportOutstanding
from oathlink.services.report.record import reportRecord
from oathlink.services.report.history import reportHistory
from oathlink.util.https.https import get as getData, put as putData

def hello(certificateFilename: str, keyFilename: str) -> str:
    return helloOathlink(certificateFilename=certificateFilename, keyFilename=keyFilename)

def data_upload(oathLink: str, filename: str) -> bool:
    return putData(url=oathLink, filename=filename)

def data_download(oathLink: str, filename: str = '') -> str:
    return getData(url=oathLink, filename=filename)

def upload(certificateFilename: str, keyFilename: str, userId: str, ownerId: str, ownerAuthorization: str = '',
           description: str = '', intent: str = '') -> tuple[str, str]:
    return getOathlinkUpload(certificateFilename=certificateFilename, keyFilename=keyFilename, userId=userId,
                             ownerId=ownerId, ownerAuthorization=ownerAuthorization, description=description,
                             intent=intent)

def download(certificateFilename: str, keyFilename: str, oathId: str) -> str:
    return getOathlinkDownload(certificateFilename=certificateFilename, keyFilename=keyFilename, oathId=oathId)

def decrypt(oathIdEncrypted: str, oathSecret: str) -> str:
    return decryptOathId(oathIdEncrypted=oathIdEncrypted, oathSecret=oathSecret)

def archive(certificateFilename: str, keyFilename: str, recordId: [str, list] = None) -> list:
    return archiveOathlink(certificateFilename=certificateFilename, keyFilename=keyFilename, recordId=recordId)

def cancel(certificateFilename: str, keyFilename: str, recordId: [str, list] = None) -> list:
    return cancelOathlink(certificateFilename=certificateFilename, keyFilename=keyFilename, recordId=recordId)

def agent_create(certificateFilename: str, keyFilename: str, serial: str, description: str) -> str:
    return createAgent(certificateFilename=certificateFilename, keyFilename=keyFilename, serial=serial, description=description)

def agent_ip_add(certificateFilename: str, keyFilename: str, ip: str) -> str:
    return addIP(certificateFilename=certificateFilename, keyFilename=keyFilename, ip=ip)

def agent_ip_remove(certificateFilename: str, keyFilename: str, ip: str) -> str:
    return removeIP(certificateFilename=certificateFilename, keyFilename=keyFilename, ip=ip)

def agent_link(certificateFilename: str, keyFilename: str, userId: str) -> str:
    return linkAgents(certificateFilename=certificateFilename, keyFilename=keyFilename, userId=userId)

def agent_unlink(certificateFilename: str, keyFilename: str, userId: str) -> str:
    return unlinkAgents(certificateFilename=certificateFilename, keyFilename=keyFilename, userId=userId)

def report_record(certificateFilename: str, keyFilename: str, recordId: [str, list] = None) -> list:
    return reportRecord(certificateFilename=certificateFilename, keyFilename=keyFilename, recordId=recordId)

def report_history(certificateFilename: str, keyFilename: str, recordId: [str, list] = None) -> str:
    return reportHistory(certificateFilename=certificateFilename, keyFilename=keyFilename, recordId=recordId)

def report_outstanding(certificateFilename: str, keyFilename: str) -> str:
    return reportOutstanding(certificateFilename=certificateFilename, keyFilename=keyFilename)
