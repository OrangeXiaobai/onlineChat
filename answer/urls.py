from django.urls import path
from .views import chat, export_image_with_logo

urlpatterns = [
    path('chat/', chat, name='chat'),
    path('addlogo/', export_image_with_logo, name='addlogo'),
]