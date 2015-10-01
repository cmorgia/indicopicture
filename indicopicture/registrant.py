from MaKaC.registration import Registrant
from MaKaC.webinterface import urlHandlers


def getPicture(self):
    return self.picture


def setPicture(self,picture):
    self.picture = picture
    self.pictureURL = urlHandlers.UHRegistrantAttachmentFileAccess.getURL(self.picture).url


def getPictureURL(self):
    return self.pictureURL


Registrant.getPicture = getPicture
Registrant.getPictureURL = getPictureURL
Registrant.setPicture = setPicture
