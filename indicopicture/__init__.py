# coding=utf-8
from cStringIO import StringIO

from flask import request
from webassets import Bundle
import os

from indico.util.i18n import _
from MaKaC.PDFinterface.base import SimpleParagraph
from MaKaC.webinterface.pages.registrants import WRegistrantModifMain, WConfModifRegistrantMiscInfoModify
from MaKaC.PDFinterface.base import Image as PDFImage
from indico.MaKaC.badgeDesignConf import ItemAware
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.core import signals
from indico.core.config import Config
import MaKaC.webinterface.urlHandlers as urlHandlers
from MaKaC.webinterface.common.baseNotificator import TplVar
from MaKaC.webinterface.common.registrantNotificator import Notificator
from MaKaC.registration import Registrant, FileInput, FieldInputs, FieldInputType
from MaKaC.webinterface.pages.registrationForm import WFileInputField
from MaKaC.badgeDesignConf import BadgeDesignConfiguration
from indico.core.fossils.registration import IRegFormGeneralFieldFossil, IRegFormFileInputFieldFossil, \
    IRegFormRegistrantBasicFossil
from indico.web.http_api.hooks.registration import RegistrantFetcher
import indicopicture.http_api.hooks
import indicopicture.registrant

blueprint = IndicoPluginBlueprint('indicopicture', __name__)


class IndicoPicturePlugin(IndicoPlugin):
    """Indico Picture Plugin

    """
    configurable = False

    def init(self):
        super(IndicoPicturePlugin, self).init()

        # Inject the PictureInput as available field in the UI
        inputs = FieldInputs.getAvailableInputs()
        inputs[PictureInput.getId()] = PictureInput
        taggedValue  = IRegFormGeneralFieldFossil.get('getValues').getTaggedValue('result')
        taggedValue["indicopicture.PictureInput"]=IRegFormFileInputFieldFossil

        RegistrantFetcher.DETAIL_INTERFACES["basic"]=IPictureFossil

        # Inject the JS and CSS, should be in limited pages
        self.inject_js('indicopicture_js')
        self.inject_css('indicopicture_css')


    def register_tpl_bundle(self, name, *files):
        def noop(_in, out, **kw):
            out.write(_in.read())
        bundle = Bundle(*files, filters=(noop,), output='tpls/{}'.format(name))
        fileName = bundle.resolve_output(self.assets)
        if os.path.isfile(fileName):
            os.remove(fileName)
        bundle.build(self.assets,force=False,disable_cache=True)
        self.assets.register(name, bundle)

    def register_assets(self):
        self.register_js_bundle('indicopicture_js', 'js/indicopicture.js','js/lib/webcam.js')
        self.register_css_bundle('indicopicture_css', 'css/test.css')
        self.register_tpl_bundle('picture.tpl.html','tpls/picture.tpl.html')
        self.register_tpl_bundle('webcam.tpl.html','tpls/webcam.tpl.html')


    def get_blueprints(self):
        return blueprint

    @signals.app_created.connect
    def _config(app, **kwargs):
        pass

class placeholder():
    __name__ = 'indicopicture'
    """
    """


class WPictureInputField(WFileInputField):
    _for_module = placeholder()

    def getVars(self):
        wvars = WFileInputField.getVars(self)
        wvars["field"] = self._field

        htmlName = self._field.getHTMLName()
        value = self._default

        if self._item is not None:
            value = self._item.getValue() if self._item.getValue() else None
            htmlName = self._item.getHTMLName()

        wvars["value"] = value
        wvars["htmlName"] = htmlName
        return wvars

class FileUpload():
    def __init__(self,file,name):
        self.file=file
        self.filename = name


class PictureInput(FileInput):
    _id = "picture"
    _icon = "icon-file"
    _label = "Picture"
    _directives = "nd-picture-field"

    def getName(cls):
        return "Picture"
    getName = classmethod(getName)

    def getValueDisplay(self, value):
        uh = (urlHandlers.UHRegistrantAttachmentFileAccess if request.blueprint == 'event_mgmt' else
              urlHandlers.UHFileAccess)
        url = uh.getURL(value)
        fileName = value.getFileName()

        return """<a href="%s" class="claudio">%s</a>
                <div style="position: absolute; top:150px; right:200px"><img style="width: 225px; " src="%s"></div> """ % (uh.getURL(value), value.getFileName(),uh.getURL(value))

    def _getModifHTML(self, item, registrant, default=None):

        wc = WPictureInputField(self, item, default)
        return wc.getHTML()

    def preprocessImage(self,file):
        import PIL
        from PIL import Image
        out = StringIO()
        img = Image.open(file)
        basesize = 240,240
        img.thumbnail(basesize,PIL.Image.ANTIALIAS)
        img.save(out,"jpeg")
        return out

    def _setResponseValue(self, item, params, registrant, override=False, validate=True):
        v = params.get(self.getHTMLName(), "")
        if 'import' in params:
            v = params.get(item.getGeneralField().getCaption(), "")

        newValueEmpty = v.strip() == "" if isinstance(v, str) else v.filename == ""

        if 'picture_uri' in params and params['picture_uri']!="": # case picture from webcam snapshot
            from indico.util.data_uri import DataURI
            data_uri = DataURI(params['picture_uri']).data
            #file = self.preprocessImage(StringIO(data_uri))
            file=StringIO(data_uri)
            v = FileUpload(file,"reg"+self._id+".jpg")
            newValueEmpty = False

        params[self.getHTMLName()]=v
        FileInput._setResponseValue(self,item,params,registrant,override,validate)

        # There is no Picture: CREATE IT
        if newValueEmpty:
            f = self.createDefaultPicture(registrant)
            item.setValue(f)

        registrant.setPicture(item.getValue())

    def _getSpecialOptionsHTML(self):
        return ""

    def clone(self, gf):
        ti = FieldInputType.clone(self, gf)
        return ti

    def createDefaultPicture(self,registrant):
        try:
            from unogcore import UnogCorePlugin
            no_image_path = UnogCorePlugin.root_path + "/static/images/no_image.png"
        except:
            no_image_path = os.path.join(Config.getInstance().getHtdocsDir(), "images", "popup_close_button.png")

        fileUploaded = FileUpload(open(no_image_path,'r'),"picture" + str(registrant.getId())+".png")
        file = registrant.saveFile(fileUploaded)

        return file

class PictureTplVar(TplVar):
    _name = "registrant_picture"
    _description = ""

    @classmethod
    def getValue(cls, registrant):
        return registrant.getPicture()

Notificator.getVarList().append(PictureTplVar)


class Picture(ItemAware):

    @classmethod
    def getArgumentType(cls):
        return Registrant

    @classmethod
    def getValue(cls, reg):
        from reportlab.lib.units import cm
        # set picture height like width
        index, badgeTemplate = reg.getBadgeTemplate()
        item = cls._item
        pWidth = badgeTemplate.pixelsToCm(item.getWidth()) * cm
        pHeight = pWidth
        text = reg.getPicture()
        if(text):
            p = PDFImage(filename=text.getFilePath(),width=pWidth,height=pHeight)
        else:
            p = SimpleParagraph("NO PICTURE")
        return p


def decorateBadgeDesignConfiguration(fn):
    def new_funct(*args, **kwargs):
        ret = fn(*args, **kwargs)
        self = args[0]
        self.items_actions["Picture"]=(_("Picture"), Picture)
        for item in self.groups:
            if item[0]=='Registrant Data':
                if 'Picture' not in item[1]:
                    item[1].append('Picture')
    return new_funct
BadgeDesignConfiguration.__init__ = decorateBadgeDesignConfiguration(BadgeDesignConfiguration.__init__)


def decorateGetVars(fn):
    def new_funct(*args, **kwargs):
        ret = fn(*args, **kwargs)
        self = args[0]
        ret["registrantPictureUrl"]=self._registrant.getPictureURL()
        return ret
    return new_funct

WRegistrantModifMain.getVars = decorateGetVars(WRegistrantModifMain.getVars)
WConfModifRegistrantMiscInfoModify.getVars = decorateGetVars(WConfModifRegistrantMiscInfoModify.getVars)

class IPictureFossil(IRegFormRegistrantBasicFossil):
    def getPictureURL(self):
        """
        Get picture URL
        """
    getPictureURL.result = lambda x: x.getPictureURL() if isinstance(x,Registrant) else ""
