from django.urls import path
from . import views
app_name = "payments"

urlpatterns = [
    path("process/", views.process_payment, name="payment_process"),
    path("callback/", views.callback_getaway_view, name="payment_callback"),
]