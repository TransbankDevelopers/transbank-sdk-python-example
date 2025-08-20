from django.urls import path
from webpay_plus import views

app_name = 'webpay_plus'

urlpatterns = [
    path('', views.create, name='create'),
    path('commit', views.commit, name='commit'),
    path('refund', views.refund, name='refund'),
    path('status', views.status, name='status'),
]
