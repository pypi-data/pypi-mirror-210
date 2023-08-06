from drf_spectacular.utils import extend_schema

from kfsd.apps.endpoints.views.docs.v1.outpost import OutpostV1Doc
from kfsd.apps.endpoints.serializers.common.outpost import OutpostViewModelSerializer
from kfsd.apps.endpoints.serializers.base import NotFoundSerializer, ErrorSerializer


class OutpostDoc:
    @staticmethod
    def modelviewset():
        return {
            "list": extend_schema(**OutpostDoc.modelviewset_list()),
            "retrieve": extend_schema(**OutpostDoc.modelviewset_get()),
            "destroy": extend_schema(**OutpostDoc.modelviewset_delete()),
            "partial_update": extend_schema(**OutpostDoc.modelviewset_patch()),
            "create": extend_schema(**OutpostDoc.modelviewset_create()),
        }

    @staticmethod
    def modelviewset_patch():
        return {
            "summary": "Outpost - Patch",
            "description": "Outpost Patch",
            "tags": ["OUTPOST"],
            "responses": {
                200: OutpostViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": OutpostV1Doc.modelviewset_patch_path_examples(),
            "examples": OutpostV1Doc.modelviewset_patch_examples(),
        }

    @staticmethod
    def modelviewset_list():
        return {
            "summary": "Outpost - List",
            "description": "Outpost - All",
            "tags": ["OUTPOST"],
            "responses": {
                200: OutpostViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": OutpostV1Doc.modelviewset_list_path_examples(),
            "examples": OutpostV1Doc.modelviewset_list_examples(),
        }

    @staticmethod
    def modelviewset_get():
        return {
            "summary": "Outpost - Get",
            "description": "Outpost Detail",
            "tags": ["OUTPOST"],
            "responses": {
                200: OutpostViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": OutpostV1Doc.modelviewset_get_path_examples(),
            "examples": OutpostV1Doc.modelviewset_get_examples(),
        }

    @staticmethod
    def modelviewset_create():
        return {
            "summary": "Outpost - Create",
            "description": "Outpost - Create",
            "tags": ["OUTPOST"],
            "responses": {
                200: OutpostViewModelSerializer,
                400: ErrorSerializer,
                404: ErrorSerializer,
                500: ErrorSerializer,
            },
            "examples": OutpostV1Doc.modelviewset_create_examples(),
        }

    @staticmethod
    def modelviewset_delete():
        return {
            "summary": "Outpost - Delete",
            "description": "Outpost Delete",
            "tags": ["OUTPOST"],
            "responses": {204: None, 404: NotFoundSerializer, 500: ErrorSerializer},
            "parameters": OutpostV1Doc.modelviewset_delete_path_examples(),
        }
