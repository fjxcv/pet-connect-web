"""
模块说明：portal 模块 URL 路由。
"""

from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import PortalCarouselViewSet, PortalDashboardView, PortalStatsView

router = DefaultRouter()

router.register(r'carousel', PortalCarouselViewSet, basename='portal-carousel')

urlpatterns = [

    path('stats/', PortalStatsView.as_view(), name='portal-stats'),

    path('dashboard/', PortalDashboardView.as_view(), name='portal-dashboard'),

] + router.urls

