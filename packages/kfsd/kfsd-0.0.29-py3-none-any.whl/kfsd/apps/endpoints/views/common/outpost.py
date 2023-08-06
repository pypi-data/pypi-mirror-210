from drf_spectacular.utils import extend_schema_view

from kfsd.apps.models.tables.outpost import Outpost
from kfsd.apps.endpoints.serializers.common.outpost import OutpostViewModelSerializer
from kfsd.apps.endpoints.views.docs.outpost import OutpostDoc
from kfsd.apps.endpoints.views.common.custom_model import CustomModelViewSet


@extend_schema_view(**OutpostDoc.modelviewset())
class OutpostModelViewSet(CustomModelViewSet):
    queryset = Outpost.objects.all()
    serializer_class = OutpostViewModelSerializer
