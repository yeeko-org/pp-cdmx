from rest_framework import routers
from django.conf.urls import url, include

from project.api.views import (FinalProjectView)

urlpatterns = [
    url(r'^final_project/(?P<period_id>[-\d]+)/$',
        FinalProjectView.as_view()),
]
