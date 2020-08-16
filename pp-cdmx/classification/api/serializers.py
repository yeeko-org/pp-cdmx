# -*- coding: utf-8 -*-
from rest_framework import serializers

from classification.models import (CategoryIECM, )


class CategoryIECMSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryIECM
        fields = "__all__"
        # depth = 2

