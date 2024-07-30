from django.urls import path
from api.views import *

# user
urlpatterns = [
    path('users/register/', register, name='register'),
    path('users/login/', login, name='login'),
    path('users/get/', get_users, name='get_users'),
    path('users/delete/<int:pk>/', delete_user, name='delete_user'),
    path('users/update/<int:pk>/', update_user, name='update_user'),

    path('users/status/', get_user_status, name='get_user_status')
]

# answer
urlpatterns += [
    path('answer/get', get_answer, name='get_answer'),
    path('answer/add', add_answer, name='add_answer'),
    path('answer/update', update_answer, name='update_answer'),
    path('answer/delete', delete_answer, name='delete_answer'),

    path('answer/statistics', statistics_get, name='statistics_get'),
    path('answer/process', process_get, name='process_get')
]
