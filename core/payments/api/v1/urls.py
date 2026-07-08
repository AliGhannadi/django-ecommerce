from django.urls import path
from payments.api.v1 import views

urlpatterns = [
    path("process/", views.process_payment, name="payment_process"),
    path("callback/", views.callback_getaway_view, name="payment_callback"),
]
