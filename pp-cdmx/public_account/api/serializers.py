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
