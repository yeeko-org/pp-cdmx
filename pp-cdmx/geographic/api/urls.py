from rest_framework import routers
from django.conf.urls import url, include

from geographic.api.views import (CatalogView)

# router=routers.DefaultRouter()
# router.register(r'colectivo', CollectiveList)

urlpatterns = [
    url(r'^catalog/$', CatalogView.as_view()),
    # url('', include(router.urls)),
]
