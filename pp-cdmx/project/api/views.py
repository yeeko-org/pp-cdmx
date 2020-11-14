# -*- coding: utf-8 -*-
from . import serializers
from rest_framework.response import Response
from rest_framework import (permissions, views, status)

from project.models import (FinalProject)
from period.models import PeriodPP


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
