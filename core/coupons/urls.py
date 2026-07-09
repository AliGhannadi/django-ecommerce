from django.urls import include, path

app_name = "coupons"

urlpatterns = [
    path("", include("coupons.api.v1.urls")),
]
