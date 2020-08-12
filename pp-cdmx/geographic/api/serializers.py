# -*- coding: utf-8 -*-
from rest_framework import serializers

from geographic.models import (
    TownHall, TownHallGeoData, SuburbType, Suburb, SuburbGeoData, )


class TownHallSerializer(serializers.ModelSerializer):
    # geo_point=serializers.ReadOnlyField(source="townhallgeodata.geo_point")

    class Meta:
        model = TownHall
        fields = ["id", "cve_inegi", "cve_alc", "name", "short_name", "image",
                  #"geo_point"
                  ]
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
    geo_point = serializers.ReadOnlyField(source="suburbgeodata.geo_point")

    class Meta:
        model = Suburb
        fields = [
            "id",
            "name",
            "suburb_type",
            "townhall",
            "pob_2010",
            "geo_point"]
        # depth = 2


class SuburbGeoDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuburbGeoData
        fields = "__all__"
        # depth = 2

from project.api.serializers import FinalProjectSerializer


class SuburbHeavySerializer(serializers.ModelSerializer):
    geo_data = SuburbGeoDataSerializer(source="suburbgeodata")
    final_projects = FinalProjectSerializer(many=True)

    class Meta:
        model = Suburb
        fields = "__all__"
        # depth = 2
