# -*- coding: utf-8 -*-
from . import serializers
from classification.api.serializers import CategoryIECMSerializer
from rest_framework.response import Response
from rest_framework import (permissions, views, status)

from geographic.models import (
    TownHall, TownHallGeoData, SuburbType, Suburb, SuburbGeoData, )

from classification.models import (CategoryIECM)

from api.mixins import ListMix, CreateMix, RetrieveMix
from api.mixins import MultiSerializerModelViewSet as ModelViewSet
from django.db.models import F

# class ModelList(ListMix):
#     permission_classes = [permissions.AllowAny]
#     serializer_class = serializers.ModelSerializer
#     queryset=Model.objects.all()


class CatalogView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):

        categories_queryset = CategoryIECM.objects.all()
        townhall_queryset = TownHall.objects.all()
        suburb_type_queryset = SuburbType.objects.all()
        suburb_queryset = Suburb.objects.all()\
            .order_by('townhall_id', 'suburb_type')
        data = {
            "categories": CategoryIECMSerializer(
                categories_queryset, many=True).data,
            "townhall": serializers.TownHallSerializer(
                townhall_queryset, many=True).data,
            "suburb_type": serializers.SuburbTypeSerializer(
                suburb_type_queryset, many=True).data,
            "suburb": Suburb.objects.all().values(
                "id", "name", "suburb_type", "townhall", "pob_2010")
            .annotate(geo_point = F('suburbgeodata__geo_point'))
        }
        return Response(data)


class SuburbSet(RetrieveMix):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SuburbHeavySerializer
    queryset = Suburb.objects.all()
