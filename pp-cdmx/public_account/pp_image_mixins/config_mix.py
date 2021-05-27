# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json


class PPImageMix:

    # Config
    def get_table_ref(self):
        try:
            return json.loads(self.table_ref)
        except Exception:
            return []

    def set_table_ref(self, data):
        try:
            self.table_ref = json.dumps(data)
        except Exception:
            self.table_ref = None

    def is_first_page(self):
        if "0001" in self.path:
            return True
        return False

    @property
    def period(self):
        return self.public_account.period_pp

    def reset(self):
        self.json_variables = None
        self.save()

    def get_first_image(self):
        from public_account.models import PPImage
        if self.is_first_page():
            return self
        else:
            return PPImage.objects.filter(
                public_account=self.public_account,
                path__icontains="0001",
            ).first()

    def get_table_data(self, recalculate=False):
        # cambio de logica a creacion de registro de objetos Row por ppimage
        try:
            table_data = json.loads(self.table_data)
        except Exception:
            table_data = None

        if table_data and not recalculate:
            return table_data

        self.get_data_full_image()

        self.calculate_table_data(
            limit_position=self.public_account.vertical_align_ammounts)

        try:
            return json.loads(self.table_data)
        except Exception:
            return []

    def get_json_variables(self):
        try:
            return json.loads(self.json_variables)
        except Exception:
            # print("self.json_variables No JSON object could be decoded, "
            #       "se reiniciara a { }")
            return {}
