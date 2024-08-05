from django.urls import path
from user.views import *

urlpatterns = [
    path('register/', RegisterView, name='register_page'),
    path('online', user_online, name='user_online'),
    path('userchat/<int:user_id>/', message, name='userchat'),
    path('chat/<str:room_name>/', chat_room, name='chat_room'),
]
