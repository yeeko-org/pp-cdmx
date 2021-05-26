# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class PublicAccountVisionMix:

    # calculo de referencias con vision
    def recalculate_w_manual_ref(self):
        from public_account.models import PPImage
        for image in PPImage.objects.filter(
                need_manual_ref=True,
                manual_ref__isnull=False,
                public_account=self):
            image.get_data_from_columns_mr()
        self.column_formatter_v2()
