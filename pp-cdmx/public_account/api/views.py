# -*- coding: utf-8 -*-
from . import serializers
from rest_framework import (permissions, views, status)
from rest_framework.exceptions import (
    NotFound, PermissionDenied, ValidationError)
from rest_framework.response import Response

from django.conf import settings as dj_settings

from api.mixins import MultiSerializerListRetrieveMix

from geographic.models import TownHall

from public_account.models import PublicAccount

from project.models import FinalProject


class NextView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_next_data(self):
        from public_account.models import PPImage
        from django.db.models import Q
        import json
        next_query = PPImage.objects.filter(
            Q(need_second_manual_ref=True) |
            Q(need_manual_ref=True, manual_ref__isnull=True)
        ).distinct()

        next_image = next_query.first()
        if not next_image:
            return {"msg": "sin imagenes por revisar"}
        domain = getattr(dj_settings, "URL_NEXT_SERVER", "")
        try:
            data = json.loads(next_image.manual_ref)
        except Exception as e:
            print e
            print next_image.manual_ref
            data = None
        return {
            "url": u"%s%s/%s" % (
                domain,
                next_image.public_account.period_pp.year,
                next_image.path),
            "id": next_image.id,
            "divisors": next_image.is_first_page(),
            "missing_count": next_query.count(),
            "data": data
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
            pp_image.need_second_manual_ref = False
        except Exception as e:
            raise ValidationError(
                {"errors": ["Datos de references errones", u"%s" % e]})
        pp_image.save()

        return Response(self.get_next_data())


class AmountVariationView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(serializers.AmountVariationSerializer(
            PublicAccount.objects.all(), many=True).data)


class AmountVariationTownhallView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, **kwargs):
        try:
            townhall = TownHall.objects.get(id=kwargs.get("townhall_id"))
        except Exception as e:
            raise NotFound()
        final_projects = FinalProject.objects\
            .filter(suburb__townhall=townhall)
        return Response(serializers.AmountVariationSuburbsSerializer(
            final_projects, many=True).data)


class PublicAccountSetView(MultiSerializerListRetrieveMix):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.PublicAccountList
    queryset = PublicAccount.objects.all()\
        .prefetch_related("townhall", "period_pp")

    def get_queryset(self):
        from django.db.models import Q
        orphan_rows = self.request.query_params.get("orphan_rows")
        match_review = self.request.query_params.get("match_review")
        queryset = self.queryset
        if orphan_rows:
            if orphan_rows.lower() in ["si", "true"]:
                queryset = queryset.filter(orphan_rows__isnull=False)\
                    .exclude(Q(orphan_rows="") | Q(orphan_rows="[]"))

        if match_review:
            if match_review.lower() in ["si", "true"]:
                queryset = queryset.filter(match_review=True)
            elif match_review.lower() in ["no", "false"]:
                queryset = queryset.exclude(match_review=True)

        return queryset


class OrphanRowsView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, request, **kwargs):
        try:
            public_account = PublicAccount.objects.get(
                id=kwargs.get("public_account_id"))
        except Exception as e:
            raise NotFound()
        return public_account

    def get(self, request, **kwargs):
        from project.models import FinalProject
        from project.api.serializers import FinalProjectOrphanSerializer
        public_account = kwargs.get(
            "public_account", self.get_object(request, **kwargs))

        fp_query = FinalProject.objects\
            .filter(
                suburb__townhall=public_account.townhall,
                period_pp=public_account.period_pp,
                image__isnull=True)\
            .order_by("suburb__short_name")\
            .prefetch_related("project", "suburb")

        final_projects = FinalProjectOrphanSerializer(fp_query, many=True)

        return Response({
            "public_account_id": public_account.id,
            "comment_match": public_account.comment_match,
            "orphan_rows": public_account.get_orphan_rows(),
            "final_projects": final_projects.data
        })

    def post(self, request, **kwargs):
        from scripts.data_cleaner_v2 import saveFinalProjSuburb_v2
        public_account = self.get_object(request, **kwargs)
        orphan_rows = public_account.get_orphan_rows()
        seqs = {data.get("seq"): data for data in orphan_rows}
        done_seqs = []
        match_review = request.data.get("match_review")
        comment_match = request.data.get("comment_match")

        for match in request.data.get("matches", []):
            suburb = match.get("suburb")
            seq = match.get("seq")
            seq_data = seqs.get(seq)
            if not seq_data:
                continue

            saveFinalProjSuburb_v2(suburb, seq_data, simil=-1)
            done_seqs.append(seq)

        orphan_rows = [seq_data for seq, seq_data in seqs.items()
                       if not seq in done_seqs]
        if match_review == True:
            public_account.match_review = True
        elif match_review == False:
            public_account.match_review = False
        public_account.set_orphan_rows(orphan_rows)
        public_account.comment_match = comment_match
        public_account.set_manual_macth(request.data)
        public_account.save()
        kwargs["public_account"] = public_account

        return self.get(request, **kwargs)
