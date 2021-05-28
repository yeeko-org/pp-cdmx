# -*- coding: utf-8 -*-
from rest_framework import serializers

from public_account.models import (PublicAccount, PPImage, Row)

from project.models import FinalProject
from geographic.api.serializers import SuburbFullSerializer


class AmountVariationSerializer(serializers.ModelSerializer):

    def get_no_info(self, public_account):
        return ""

    class Meta:
        model = PublicAccount
        fields = [
            "townhall",
            "period_pp",

            "approved_mean",
            "executed_mean",

            "minus_10",
            "minus_5",
            "similar",
            "plus_5",

            "not_executed",
            "no_info",
        ]
        # depth = 2


class AmountVariationSuburbsSerializer(serializers.ModelSerializer):
    suburb = SuburbFullSerializer()

    class Meta:
        model = FinalProject
        fields = [
            "period_pp",
            "approved",
            "executed",
            "variation_calc",
            "range",
            "suburb",
        ]
        # depth = 2


from geographic.api.serializers import TownHallSerializer, PeriodPPSerializer


class PPImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PPImage
        fields = [
            "id",
            "validated",
            "path",
        ]


class PPImageUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PPImage
        fields = [
            "id",
            "validated",
            "path",
            "comments"
        ]
        read_only_fields = ["path"]


class PublicAccountList(serializers.ModelSerializer):
    #townhall = TownHallSerializer()
    townhall = serializers.ReadOnlyField(source="townhall.name")
    period_pp = serializers.ReadOnlyField(source="period_pp.year")
    # period_pp = PeriodPPSerializer()
    pp_images = PPImageSerializer(many=True)

    class Meta:
        model = PublicAccount
        fields = [
            "id",
            "townhall",
            "period_pp",
            "status",
            "match_review",
            "suburb_count",
            #"orphan_rows_count",
            "pp_images"
        ]


class PublicAccountRetrieve(serializers.ModelSerializer):

    class Meta:
        model = PublicAccount
        fields = [
            "id",
            "townhall_id",
            "townhall",
            "period_pp",
            "status"
        ]


class RowSerializer(serializers.ModelSerializer):
    formatted_data = serializers.ReadOnlyField(source="get_formatted_data")
    vision_data = serializers.ReadOnlyField(source="get_vision_data")
    errors = serializers.ReadOnlyField(source="get_errors")

    class Meta:
        model = Row
        fields = [
            "id",
            "final_project",
            "project_name",
            "description",
            "progress",
            "approved",
            "modified",
            "executed",
            "variation",
            "validated",
            "similar_suburb_name",
            "variation_calc",
            "range",
            "errors",
            "sequential",
            "vision_data",
            "formatted_data",
            "top",
            "bottom",
        ]
        read_only_fields = [
            "similar_suburb_name",
            "variation_calc",
            "range",
            "errors",
            "sequential",
            "vision_data",
            "formatted_data",
            "top",
            "bottom",
        ]


class PPImageSimpleSerializer(PublicAccountList):
    json_variables = serializers.SerializerMethodField()

    def get_json_variables(self, obj):
        try:
            return obj.get_json_variables()
        except Exception as e:
            return None
    manual_ref = serializers.SerializerMethodField()

    def get_manual_ref(self, obj):
        try:
            return obj.get_manual_ref()
        except Exception as e:
            return None

    class Meta:
        model = PPImage
        fields = [
            "id",
            "path",
            "json_variables",
            "manual_ref",
            "table_ref_columns",
        ]
