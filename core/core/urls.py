"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.http import HttpResponse



def trigger_error(request):
   division_by_zero = 1 / 0

urlpatterns = [
    # admin panel url
    path("admin/", admin.site.urls),
    
    # accounts urls
    path("accounts/",include("accounts.urls"), name="accounts"),

    # products urls
    path("products/", include("products.urls"), name="products"),

    # cart urls
    path("cart/", include("cart.urls"), name="carts"),

    # orders urls
    path("orders/", include("orders.urls"), name="orders"),

    # payments urls
    path("payments/", include("payments.urls"), name="payments"),

    # social urls
    path("social/", include("social.urls"), name="social"),
    
    path('api-auth/', include('rest_framework.urls')),
    
    # sentry debug test
    # path('sentry-debug/', trigger_error),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


if settings.SHOW_DEBUGGER_TOOLBAR:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls')),
                    ]

if settings.SHOW_SWAGGER:
    urlpatterns += [
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'),
             name='swagger-ui'),
    ]


