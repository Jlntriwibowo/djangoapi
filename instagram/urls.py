from django.urls import path
from .views import DownloadFollowers

urlpatterns = [
    path('download_followers/', DownloadFollowers.as_view(), name='download_followers'),
]
