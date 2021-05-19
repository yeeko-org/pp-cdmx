# -*- coding: utf-8 -*-
from rest_framework import serializers

from public_account.models import (PublicAccount, PPImage)

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
    townhall = TownHallSerializer()
    period_pp = serializers.ReadOnlyField(source="period_pp.year")
    # period_pp = PeriodPPSerializer()
    orphan_rows_count = serializers.SerializerMethodField()
    pp_images = PPImageSerializer(many=True)
    def get_orphan_rows_count(self, obj):
        try:
            return len(obj.get_orphan_rows())
        except Exception as e:
            return None
    class Meta:
        model= PublicAccount
        fields = [
            "id",
            "townhall",
            "period_pp",
            "status",
            "match_review",
            "suburb_count",
            "orphan_rows_count",
            "pp_images"
        ]

class PublicAccountRetrieve(PublicAccountList):
    class Meta:
        model= PublicAccount
        fields = [
            "id",
            "townhall_id",
            "townhall",
            "period_pp",
            "status"
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
    table_data = serializers.SerializerMethodField()
    def get_table_data(self, obj):
        try:
            return obj.get_table_data()
        except Exception as e:
            return None

    table_ref = serializers.SerializerMethodField()
    def get_table_ref(self, obj):
        try:
            return obj.get_table_ref()
        except Exception as e:
            return None

    class Meta:
        model= PPImage
        fields = [
            "id",
            "path",
            "json_variables",
            "table_data",
            "table_ref",
            "manual_ref",
        ]