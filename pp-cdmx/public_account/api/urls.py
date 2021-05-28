from django.conf.urls import include, url

from rest_framework import routers

from .views import (
    AmountVariationTownhallView, AmountVariationView, ImageRefsView, NextView,
    OrphanRowsView, PPImageSetView, PublicAccountSetView, RowSetView)

router = routers.DefaultRouter()
router.register(r"image", PPImageSetView)
router.register(r"row", RowSetView)
router.register(r"", PublicAccountSetView)

urlpatterns = [
    url(r'^next/$', NextView.as_view()),
    url(r'^(?P<public_account_id>[-\d]+)/orphan_rows/$',
        OrphanRowsView.as_view()),
    url(r'^image/(?P<image_id>[-\d]+)/refs/$', ImageRefsView.as_view()),
    url(r'^amount_variation/$', AmountVariationView.as_view()),
    url(r'^amount_variation/(?P<townhall_id>[-\d]+)/$',
        AmountVariationTownhallView.as_view()),
    url('', include(router.urls)),
]
