"""
cms 视图：分类管理、文章 CRUD + 收藏、我的收藏、公告专区。
"""

from django.utils import timezone
from django.db.models import Q, F
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from common.permissions import IsActiveUser, IsAdminRole
from .models import ArticleFavorite, CmsArticle, CmsCategory
from .serializers import (
    ArticleFavoriteItemSerializer,
    CmsArticleSerializer,
    CmsCategorySerializer,
)


class CmsCategoryViewSet(viewsets.ModelViewSet):
    """
    功能：文章分类管理。
    【权限】list/retrieve：visitor；其余：admin
    """
    queryset = CmsCategory.objects.all()
    serializer_class = CmsCategorySerializer

    def get_permissions(self):
        # 分支：游客可读分类；写操作仅 admin
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]


class CmsArticleViewSet(viewsets.ModelViewSet):
    """
    功能：文章 CRUD + 收藏动作。
    【权限】list/retrieve：visitor；favorite：user；其余：admin
    """
    queryset = CmsArticle.objects.select_related('category', 'author').all()
    serializer_class = CmsArticleSerializer

    def get_permissions(self):
        # 分支：list/retrieve 公开；favorite 需要登录+未封禁；其余 admin
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'favorite':
            return [permissions.IsAuthenticated(), IsActiveUser()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = super().get_queryset()
        article_type = self.request.query_params.get('type')
        category_id = self.request.query_params.get('category')
        search_q = (self.request.query_params.get('search') or '').strip()
        if article_type:
            qs = qs.filter(article_type=article_type)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if search_q:
            qs = qs.filter(
                Q(title__icontains=search_q) | Q(summary__icontains=search_q) | Q(content__icontains=search_q)
            )
        # 分支：非 admin 的 list/retrieve 只返回已发布（status=1）的文章
        if self.action in ['list', 'retrieve'] and not (self.request.user.is_authenticated and getattr(self.request.user.profile, 'role', None) == 'admin'):
            qs = qs.filter(status=1)
        return qs

    def perform_create(self, serializer):
        """
        功能：创建文章时自动设置 author 为当前用户。
        【权限】admin
        """
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        功能：详情接口，status=1 时阅读量 +1。
        """
        instance = self.get_object()
        if instance.status == 1:
            CmsArticle.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
            instance.refresh_from_db()
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        功能：更新时若首次发布则自动填充 published_at。
        """
        article = serializer.save()
        if article.status == 1 and not article.published_at:
            article.published_at = timezone.now()
            article.save(update_fields=['published_at'])

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """
        功能：收藏/取消收藏（仅 status=1 的文章可收藏）。
        【权限】user
        """
        article = self.get_object()
        if article.status != 1:
            return Response(
                {'detail': '仅可收藏已发布的文章'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == 'POST':
            ArticleFavorite.objects.get_or_create(article=article, user=request.user)
            return Response({'detail': 'Favorited'})
        ArticleFavorite.objects.filter(article=article, user=request.user).delete()
        return Response({'detail': 'Favorite removed'})


class MyArticleFavoritesView(APIView):
    """
    功能：我的收藏列表（仅 status=1 的文章）。
    【权限】user（需登录未封禁）
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def get(self, request):
        favorites = (
            ArticleFavorite.objects.filter(user=request.user, article__status=1)
            .select_related('article', 'article__category', 'article__author')
            .order_by('-created_at')
        )
        serializer = ArticleFavoriteItemSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)


class CmsAnnouncementView(APIView):
    """
    功能：公告专区（type=announcement, status=1）。
    【权限】visitor/user/admin 均可访问
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        announcements = CmsArticle.objects.filter(
            article_type='announcement', status=1
        ).select_related('category', 'author').order_by('-is_pinned', '-published_at')
        serializer = CmsArticleSerializer(announcements, many=True, context={'request': request})
        return Response(serializer.data)
