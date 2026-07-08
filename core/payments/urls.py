from django.urls import include, path

app_name = "payments"

urlpatterns = [
    path("", include("payments.api.v1.urls"))
]
