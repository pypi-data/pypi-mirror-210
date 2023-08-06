from kfsd.apps.core.utils.http.django.cookie import Cookie


class DjangoRequest():
    def __init__(self, request=None):
        self.__request = request
        self.__djangoCookies = Cookie(request)

    def getRequest(self):
        return self.__request

    def getDjangoReqCookies(self):
        return self.__djangoCookies

    def parseInputData(self, serializer, raiseExceptions=True):
        inputSerializer = serializer(data=self.__request.data)
        inputSerializer.is_valid(raise_exception=raiseExceptions)
        return inputSerializer.data
