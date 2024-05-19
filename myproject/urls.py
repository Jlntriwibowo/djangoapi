# myproject/urls.py
from django.contrib import admin
from django.urls import path
from instagram.views import DownloadFollowers

urlpatterns = [
    path('admin/', admin.site.urls),
    path('download_followers/', DownloadFollowers.as_view(), name='download_followers'),
]
