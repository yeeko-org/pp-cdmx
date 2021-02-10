# -*- coding: utf-8 -*-
from . import serializers
from rest_framework import (permissions, views, status)
from rest_framework.exceptions import (
    NotFound, PermissionDenied, ValidationError)
from rest_framework.response import Response
from django.conf import settings as dj_settings


class NextView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_next_data(self):
        from public_account.models import PPImage
        next_query = PPImage.objects.filter(
            need_manual_ref=True, manual_ref__isnull=True)
        next_image = next_query.first()
        if not next_image:
            return {"msg": "sin imagenes por revisar"}
        domain = getattr(dj_settings, "URL_NEXT_SERVER", "")
        return {
            "url": u"%s%s/%s" % (
                domain,
                next_image.public_account.period_pp.year,
                next_image.path),
            "id": next_image.id,
            "divisors": next_image.is_first_page(),
            "missing_count": next_query.count(),
        }

    def get(self, request):
        return Response(self.get_next_data())

    def post(self, request):
        import json
        from public_account.models import PPImage
        try:
            pp_image = PPImage.objects.get(id=request.data.get("id"))
        except Exception as e:
            raise ValidationError(
                {"errors": ["Imagen no encontrada", u"%s" % e]})

        references = request.data.get("references")
        if not isinstance(references, list) or not references:
            raise ValidationError(
                {"errors": ["se esperava una lista en references"]})

        divisors = request.data.get("divisors")
        if divisors:
            if not isinstance(divisors, list):
                raise ValidationError(
                    {"errors": ["se esperava una lista en divisors"]})

        try:
            pp_image.manual_ref = json.dumps(
                {
                    "references": references,
                    "divisors": divisors
                })
        except Exception as e:
            raise ValidationError(
                {"errors": ["Datos de references errones", u"%s" % e]})
        pp_image.save()

        return Response(self.get_next_data())
