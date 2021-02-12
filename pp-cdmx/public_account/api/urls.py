from rest_framework import routers
from django.conf.urls import url, include

from .views import (NextView, AmountVariationView, AmountVariationTownhallView)

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^next/$', NextView.as_view()),
    url(r'^amount_variation/$', AmountVariationView.as_view()),
    url(r'^amount_variation/(?P<townhall_id>[-\d]+)/$',
        AmountVariationTownhallView.as_view()),
    url('', include(router.urls)),
]
