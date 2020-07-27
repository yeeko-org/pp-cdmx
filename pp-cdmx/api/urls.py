from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework.authtoken import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^token-auth/', views.obtain_auth_token),

    # Endpoints
    url(r'^geo/', include('geographic.api.urls')),
]
