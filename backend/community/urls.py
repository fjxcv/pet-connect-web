"""
模块说明：community 模块 URL 路由。
"""

from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import CommunityCommentViewSet, CommunityPostViewSet, MyPostFavoritesView

router = DefaultRouter()

router.register(r'posts', CommunityPostViewSet, basename='community-post')

comment_like = CommunityCommentViewSet.as_view({'post': 'like', 'delete': 'like'})

comment_destroy = CommunityCommentViewSet.as_view({'delete': 'destroy'})

urlpatterns = [

    path('favorites/', MyPostFavoritesView.as_view(), name='community-favorites'),

    path('comments/<int:pk>/', comment_destroy, name='comment-destroy'),

    path('comments/<int:pk>/like/', comment_like, name='comment-like'),

] + router.urls
