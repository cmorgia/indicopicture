from base import BaseRegistrantsHook


class RegistrantsHook(BaseRegistrantsHook):
    RE = r'(?P<event>[\w\s]+)/registrants'


class RegistrantsBySessionHook(BaseRegistrantsHook):
    RE = r'(?P<event>[\w\s]+)/session/(?P<session>[\w\s]+)/registrants'

    def _getParams(self):
        super(RegistrantsBySessionHook, self)._getParams()
        self._sessionId = self._pathParams['session']

    def export_registrants(self, aw,bysession=None):
        return super(RegistrantsBySessionHook, self).export_registrants(aw,self._sessionId)
