# -*- coding: utf-8 -*-
from . import serializers

from api.mixins import MultiSerializerListRetrieveUpdateMix
from api.pagination import StandardResultsSetPagination

from rest_framework import (permissions, views)
from rest_framework.response import Response

from project.models import FinalProject


class FinalProjectViewSet(MultiSerializerListRetrieveUpdateMix):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.FinalProjectSimpleSerializer
    queryset = FinalProject.objects.all()
    pagination_class = StandardResultsSetPagination


class FinalProjectView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, period_id):
        from django.db.models import Q
        final_proyect_query = FinalProject.objects\
            .filter(Q(period_pp_id=period_id) |
                    Q(period_pp__year=period_id))\
            .prefetch_related("project")
        serializer = serializers.FinalProjectSmallSerializer(
            final_proyect_query, many=True)
        return Response(serializer.data)
