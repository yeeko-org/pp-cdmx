# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import redirect
from django.views.static import serve


admin.site.site_header = u"PP-CDMX"
admin.site.site_title = u"PP-CDMX"
admin.site.index_title = u"PP-CDMX"


def redirect_admin(request):
    return redirect("/admin/")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', redirect_admin),
]


if settings.DEBUG:
    urlpatterns.append(url(r'^static/(?P<path>.*)$', serve, {
        'document_root': settings.STATIC_ROOT,
    }))
    urlpatterns.append(url(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }))
