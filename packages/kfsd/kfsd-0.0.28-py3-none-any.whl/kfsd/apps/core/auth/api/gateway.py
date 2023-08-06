from kfsd.apps.core.utils.http.base import HTTP
from kfsd.apps.core.utils.http.django.request import DjangoRequest
from kfsd.apps.core.utils.http.headers.base import Headers
from kfsd.apps.core.utils.http.headers.contenttype import ContentType
from kfsd.apps.core.common.kubefacets_config import KubefacetsConfig
from kfsd.apps.core.utils.http.django.config import DjangoConfig


class APIGateway(Headers, HTTP):
    def __init__(self, request=None):
        self.__request = DjangoRequest(request)
        self.__config = DjangoConfig(KubefacetsConfig.getSingleton().getConfig())
        Headers.__init__(self)
        HTTP.__init__(self)

    def getServicesAPIKey(self):
        return self.getDjangoConfig().findConfigs(["services.api_key"])[0]

    def getDjangoRequest(self):
        return self.__request

    def getDjangoConfig(self):
        return self.__config

    def setHttpHeaders(self):
        self.setAPIKey(self.getServicesAPIKey())
        self.setContentType(ContentType.APPLICATION_JSON)

    def httpPost(self, postUrl, payload, expStatus):
        self.setHttpHeaders()
        resp = self.post(postUrl, expStatus, json=payload, headers=self.getReqHeaders())
        return resp.json()

    def httpGet(self, getUrl, expStatus):
        self.setHttpHeaders()
        resp = self.get(getUrl, expStatus, headers=self.getReqHeaders())
        return resp.json()

    def httpDel(self, getUrl, expStatus):
        self.setHttpHeaders()
        self.delete(getUrl, expStatus, headers=self.getReqHeaders())

    def constructUrl(self, configPaths):
        uris = self.getDjangoConfig().findConfigs(configPaths)
        return self.formatUrl(uris)
