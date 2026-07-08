from django.urls import include, path

urlpatterns = [
    path("", include("products.api.v1.urls"))
]
