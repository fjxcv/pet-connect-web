"""
模块说明：cms 模块 URL 路由。
"""

from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import CmsAnnouncementView, CmsArticleViewSet, CmsCategoryViewSet, MyArticleFavoritesView

router = DefaultRouter()

router.register(r'categories', CmsCategoryViewSet, basename='cms-category')

router.register(r'articles', CmsArticleViewSet, basename='cms-article')

urlpatterns = [

    path('favorites/', MyArticleFavoritesView.as_view(), name='cms-favorites'),

    path('announcements/', CmsAnnouncementView.as_view(), name='cms-announcements'),

] + router.urls

