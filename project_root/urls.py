from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # ...existing code...
    path('qa/', include('qa.urls', namespace='qa')),
    # ...existing code...
]