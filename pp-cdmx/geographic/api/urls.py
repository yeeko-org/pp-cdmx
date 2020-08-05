from rest_framework import routers
from django.conf.urls import url, include

from geographic.api.views import (CatalogView, SuburbSet)

router = routers.DefaultRouter()
router.register(r'suburb', SuburbSet)

urlpatterns = [
    url(r'^catalog/$', CatalogView.as_view()),
    url('', include(router.urls)),
]
