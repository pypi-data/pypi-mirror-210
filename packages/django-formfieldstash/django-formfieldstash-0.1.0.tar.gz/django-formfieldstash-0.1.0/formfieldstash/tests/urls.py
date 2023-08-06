"""URLs to run the tests."""
from django.conf import settings
from django.urls import re_path
from django.contrib import admin
from django.views import static

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    ]
