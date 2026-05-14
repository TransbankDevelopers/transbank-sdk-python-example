from django.urls import path

from patpass_comercio import views

app_name = "patpass_comercio"

urlpatterns = [
    path("", views.start, name="start"),
    path("commit", views.commit, name="commit"),
    path("voucher", views.voucher, name="voucher"),
]
