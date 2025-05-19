from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls', namespace='posts')),
    path('notifications/', include('roslaw.notifications.urls', namespace='notifications')),
    path('qa/', include('roslaw.content.urls', namespace='content')),
]