from django.urls import path
from oneclick_mall import views

app_name = 'oneclick_mall'

urlpatterns = [
    path('', views.start, name='start'),
    path('finish', views.finish, name='finish'),
    path('delete', views.delete, name='delete'),
    path('authorize', views.authorize, name='authorize'),
    path('status', views.status, name='status'),
    path('refund', views.refund, name='refund'),
]
