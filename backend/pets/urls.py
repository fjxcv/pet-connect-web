"""
模块说明：pets 模块 URL 路由。
"""

from rest_framework.routers import DefaultRouter

from .views import PetProfileViewSet

router = DefaultRouter()

router.register(r'', PetProfileViewSet, basename='pet-profile')

urlpatterns = router.urls

