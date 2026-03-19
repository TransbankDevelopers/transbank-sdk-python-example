from django.urls import path
from . import views

app_name = "transaccion_completa_mall"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("installments/", views.installments, name="installments"),
    path("commit/", views.commit, name="commit"),
    path("status/", views.status, name="status"),
    path("refund/", views.refund, name="refund"),
]
