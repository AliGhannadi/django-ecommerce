from django.urls import include, path

urlpatterns = [
    path("", include("orders.api.v1.urls"))
]
