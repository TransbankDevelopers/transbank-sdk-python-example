from django.urls import path
from oneclick_mall_deferred import views

app_name = 'oneclick_mall_deferred'

urlpatterns = [
    path('', views.start, name='start'),
    path('finish', views.finish, name='finish'),
    path('authorize', views.authorize, name='authorize'),
    path('status', views.status, name='status'),
    path('capture', views.capture, name='capture'),
    path('refund', views.refund, name='refund'),
]
