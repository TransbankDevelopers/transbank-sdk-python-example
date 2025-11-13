from django.urls import path
from webpay_plus_mall_deferred import views

app_name = 'webpay_plus_mall_deferred'

urlpatterns = [
    path('', views.create, name='create'),
    path('commit', views.commit, name='commit'),
    path('refund', views.refund, name='refund'),
    path('status', views.status, name='status'),
    path('capture', views.capture, name='capture'),
]
