from django.conf.urls import url, include

from project.api.views import (FinalProjectView, FinalProjectViewSet)

from rest_framework import routers
# from project.api.views import (FinalProjectView)

router = routers.DefaultRouter()
router.register(r"final_project", FinalProjectViewSet)

urlpatterns = [
    url(r'^final_project/period/(?P<period_id>[-\d]+)/$',
        FinalProjectView.as_view()),
    url('', include(router.urls)),
]
