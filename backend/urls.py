from django.urls import path
from backend.views import *

urlpatterns = [
    path('user/', user_admin, name='user_admin'),
    path('user/edit/<int:id>/', user_edit, name='user_edit'),
    path('user/delete/<int:id>/', user_delete, name='user_delete'),

    path('answers/', answer_admin, name='answer_admin'),
    path('answers/add/', answer_add, name='answer_add'),
    path('answers/edit/<int:id>/', answer_edit, name='answer_edit'),
    path('answers/delete/<int:id>/', answer_delete, name='answer_delete'),

    path('statistics/', statistics_admin, name='statistics_admin'),

    path('userexport/', export_users_to_excel, name='user_export'),
    path('userimport/', import_users_from_excel, name='user_import'),

    path('dataexcel/', export_statistics_to_excel, name='data_excel'),
    path('dataimage/', export_statistics_to_image, name='data_image'),
]
