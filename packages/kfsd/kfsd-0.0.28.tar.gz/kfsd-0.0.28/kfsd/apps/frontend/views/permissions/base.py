from django.views.generic import View
from http import HTTPStatus
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseServerError,
    HttpResponseForbidden,
)

from kfsd.apps.core.exceptions.fe import KubefacetsFEException


class PermissionView(View):
    def verifyPermission(self, permission):
        if not permission.is_valid():
            permission.raise_exception()
        return True

    def verifyPermissionNeg(self, permission):
        if permission.is_valid():
            permission.raise_exception_neg()
        return True

    def getPermissionsClasses(self, argName):
        if hasattr(self, argName):
            return getattr(self, argName)
        return []

    def checkAllPermissions(self, request):
        for permission in self.getPermissionsClasses("permission_classes"):
            permissionObj = permission(request)
            self.verifyPermission(permissionObj)
        return True

    def checkAllPermissionsNeg(self, request):
        for permission in self.getPermissionsClasses("permission_classes_neg"):
            permissionObj = permission(request)
            self.verifyPermissionNeg(permissionObj)
        return True

    def dispatch(self, request, *args, **kwargs):
        try:
            self.checkAllPermissions(request)
            self.checkAllPermissionsNeg(request)
            return super().dispatch(request, *args, **kwargs)
        except KubefacetsFEException as ex:
            if ex.status_code == HTTPStatus.TEMPORARY_REDIRECT:
                return HttpResponseRedirect(ex.redirect_url)
            if ex.status_code == HTTPStatus.NOT_FOUND:
                return HttpResponseNotFound()
            if ex.status_code == HTTPStatus.FORBIDDEN:
                return HttpResponseForbidden()
            return HttpResponseServerError()
