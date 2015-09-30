from MaKaC.conference import ConferenceHolder
from indico.web.http_api import HTTPAPIHook
from indico.web.http_api.hooks.event import EventBaseHook
from indico.web.http_api.util import get_query_parameter


@HTTPAPIHook.register
class UpdatePictureHook(EventBaseHook):
    PREFIX = "api"
    RE = r'(?P<event>[\w\s]+)/registrant/(?P<registrant_id>[\w\s]+)/updatepicture'
    METHOD_NAME = 'api_update_picture'
    NO_CACHE = True
    COMMIT = True
    HTTP_POST = True

    def _getParams(self):
        super(UpdatePictureHook, self)._getParams()
        self._picture_payload = get_query_parameter(self._queryParams, ["picture_uri"])
        self._secret = get_query_parameter(self._queryParams, ["secret"])
        registrant_id = self._pathParams["registrant_id"]
        self._conf = ConferenceHolder().getById(self._pathParams['event'])
        self._registrant = self._conf.getRegistrantById(registrant_id)

    def _hasAccess(self, aw):
        return (self._conf.canManageRegistration(aw.getUser()) or self._conf.canModify(aw)) \
            and self._secret == self._registrant.getCheckInUUID()

    def api_update_picture(self, aw):
        try:
            from indico.util.data_uri import DataURI
            uri = DataURI(self._picture_payload)
            path = self._registrant.getPicture().getFilePath()
            data = uri.data
            _file = open(path,'w')
            _file.write(data)
            _file.close()
            return {"status": "true"}
        except:
            return {"status": "false"}