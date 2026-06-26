"""
模块说明：rescue 模块 URL 路由。
"""

from rest_framework.routers import DefaultRouter

from .views import RescueCaseViewSet

router = DefaultRouter()

router.register(r'cases', RescueCaseViewSet, basename='rescue-case')

urlpatterns = router.urls

