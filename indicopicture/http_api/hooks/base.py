from MaKaC.conference import ConferenceHolder
from MaKaC.registration import GeneralSectionForm
from indico.web.http_api.hooks.event import EventBaseHook


class BaseRegistrantsHook(EventBaseHook):
    METHOD_NAME = 'export_registrants'
    NO_CACHE = True

    def _getParams(self):
        super(BaseRegistrantsHook, self)._getParams()
        self._conf_id = self._pathParams['event']
        self._conf = ConferenceHolder().getById(self._conf_id)
        self._registrants = self._conf.getRegistrantsList()

    def _hasAccess(self, aw):
        return self._conf.canManageRegistration(aw.getUser()) or self._conf.canModify(aw)

    def export_registrants(self, aw,bysession=None):

        registrant_list = []
        for registrant in self._registrants:
            skip = False

            if bysession:
                sess = registrant.getSession(bysession)
                if sess is None:
                    skip = True
                else:
                    checkedIn = sess.isCheckedIn()
            else:
                checkedIn = registrant.isCheckedIn(),

            if not skip:
                reg = {
                    "registrant_id": registrant.getId(),
                    "checked_in": checkedIn,
                    "full_name": registrant.getFullName(title=True, firstNameFirst=True),
                    "checkin_secret": registrant.getCheckInUUID(),
                }
                if bysession:
                    reg["session"]=bysession
                regForm = self._conf.getRegistrationForm()
                reg["personal_data"] = regForm.getPersonalData().getRegistrantValues(registrant)
                registrant_list.append(reg)
        return {"registrants": registrant_list}
