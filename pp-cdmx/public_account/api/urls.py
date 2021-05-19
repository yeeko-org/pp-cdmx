from rest_framework import routers
from django.conf.urls import url, include

from .views import (
    NextView, AmountVariationView, AmountVariationTownhallView,
    PublicAccountSetView, OrphanRowsView, ImageRefsView)

router = routers.DefaultRouter()
router.register(r"", PublicAccountSetView)

urlpatterns = [
    url(r'^next/$', NextView.as_view()),
    url(r'^(?P<public_account_id>[-\d]+)/orphan_rows/$', OrphanRowsView.as_view()),
    url(r'^image/(?P<image_id>[-\d]+)/refs/$', ImageRefsView.as_view()),
    url(r'^amount_variation/$', AmountVariationView.as_view()),
    url(r'^amount_variation/(?P<townhall_id>[-\d]+)/$',
        AmountVariationTownhallView.as_view()),
    url('', include(router.urls)),
]
