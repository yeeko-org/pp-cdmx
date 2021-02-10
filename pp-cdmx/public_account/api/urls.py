from rest_framework import routers
from django.conf.urls import url, include

from .views import (NextView)

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^next/$', NextView.as_view()),
    url('', include(router.urls)),
]
