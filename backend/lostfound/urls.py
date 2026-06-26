"""
模块说明：lostfound 模块 URL 路由。
"""

from rest_framework.routers import DefaultRouter

from .views import LostFoundPostViewSet

router = DefaultRouter()

router.register(r'', LostFoundPostViewSet, basename='lost-found')

urlpatterns = router.urls

