# -*- coding: utf-8 -*-
from rest_framework import serializers

from geographic.models import (
    TownHall, TownHallGeoData, SuburbType, Suburb, SuburbGeoData, )


class TownHallSerializer(serializers.ModelSerializer):

    class Meta:
        model = TownHall
        fields = "__all__"
        # depth = 2


class TownHallGeoDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = TownHallGeoData
        fields = "__all__"
        # depth = 2


class SuburbTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuburbType
        fields = "__all__"
        # depth = 2


class SuburbSerializer(serializers.ModelSerializer):

    class Meta:
        model = Suburb
        fields = ["id", "name", "suburb_type", "townhall"]
        # depth = 2


class SuburbGeoDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuburbGeoData
        fields = "__all__"
        # depth = 2
