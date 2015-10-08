from MaKaC.registration import Registrant
from MaKaC.webinterface import urlHandlers


def getPicture(self):
    return self._picture


def setPicture(self,picture):
    self._picture = picture
    self._pictureUrl = urlHandlers.UHRegistrantAttachmentFileAccess.getURL(self._picture).url


def getPictureURL(self):
    return self._pictureUrl if hasattr(self,'_pictureUrl') else ''


Registrant.getPicture = getPicture
Registrant.getPictureURL = getPictureURL
Registrant.setPicture = setPicture
