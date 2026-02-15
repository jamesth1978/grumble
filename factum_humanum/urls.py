"""
URL configuration for factum_humanum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from factum_humanum.core import views as core_views

# Import payment_views only if stripe is available
try:
    from factum_humanum.core import payment_views
    payment_views_available = True
except ImportError:
    payment_views_available = False

urlpatterns = [
    path("", core_views.index),
    path("register/", core_views.register_work, name="register"),
    path("certificate/<uuid:work_id>/", core_views.certificate, name="certificate"),
    path("certificate/<uuid:work_id>/download/", core_views.download_certificate, name="download_certificate"),
    path("search/", core_views.search_registry, name="search_registry"),
    path("about/", core_views.about, name="about"),
    
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
]

# Add payment routes only if stripe is available
if payment_views_available:
    urlpatterns += [
        path("credits/", payment_views.buy_credits, name="buy_credits"),
        path("credits/success/", payment_views.checkout_success, name="checkout_success"),
        path("credits/cancel/", payment_views.checkout_cancel, name="checkout_cancel"),
        path("stripe/webhook/", payment_views.stripe_webhook, name="stripe_webhook"),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
