"""
portal 视图：轮播图管理 + 首页统计 + 首页聚合数据。
"""

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from common.permissions import IsAdminRole
from .models import PortalCarousel
from .serializers import PortalCarouselSerializer


class PortalCarouselViewSet(viewsets.ModelViewSet):
    """
    功能：轮播图 CRUD。
    【权限】list/retrieve：visitor 公开；其余：admin
    """
    queryset = PortalCarousel.objects.all()
    serializer_class = PortalCarouselSerializer

    def get_permissions(self):
        # 分支：list/retrieve 游客可看；create/update/delete 仅 admin
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_authenticators(self):
        if getattr(self, 'action', None) in ['list', 'retrieve']:
            return []
        return super().get_authenticators()

    def get_queryset(self):
        qs = super().get_queryset()
        # 分支：非 admin 的 list 只返回 status=1（已上线）的轮播
        if self.action == 'list' and not (
            self.request.user.is_authenticated
            and getattr(getattr(self.request.user, 'profile', None), 'role', None) == 'admin'
        ):
            qs = qs.filter(status=1)
        return qs


class PortalStatsView(APIView):
    """
    功能：首页核心统计数字（救助数、领养数、寻主中、今日上报）。
    【权限】visitor/user/admin 均可匿名访问
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.utils import timezone
        from rescue.models import RescueCase
        from pets.models import PetProfile
        from lostfound.models import LostFoundPost
        today = timezone.now().date()
        return Response({
            'total_rescued': RescueCase.objects.filter(current_status='rescued').count(),
            'total_adopted': PetProfile.objects.filter(adoption_status='adopted').count(),
            'searching_count': LostFoundPost.objects.filter(status='searching').count(),
            'today_reported': RescueCase.objects.filter(created_at__date=today).count(),
        })


class PortalDashboardView(APIView):
    """
    功能：首页聚合数据（公告 3 条 + 科普 3 条 + 紧急寻主 3 条 + 可领养宠物 4 条）。
    【权限】visitor/user/admin 均可匿名访问
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from cms.models import CmsArticle
        from cms.serializers import CmsArticleSerializer
        from lostfound.models import LostFoundPost
        from lostfound.serializers import LostFoundPostSerializer
        from pets.models import PetProfile
        from pets.serializers import PetProfileSerializer
        announcements = CmsArticle.objects.filter(
            article_type='announcement', status=1
        ).order_by('-is_pinned', '-published_at')[:3]
        science_articles = CmsArticle.objects.filter(
            article_type='science', status=1
        ).order_by('-published_at')[:3]
        urgent_lost = LostFoundPost.objects.filter(
            status='searching'
        ).order_by('-created_at')[:3]
        adoptable_pets = PetProfile.objects.filter(
            adoption_status='available', is_public=True
        ).order_by('-created_at')[:4]
        ctx = {'request': request}
        return Response({
            'announcements': CmsArticleSerializer(announcements, many=True, context=ctx).data,
            'science_articles': CmsArticleSerializer(science_articles, many=True, context=ctx).data,
            'urgent_lost': LostFoundPostSerializer(urgent_lost, many=True, context=ctx).data,
            'adoptable_pets': PetProfileSerializer(adoptable_pets, many=True, context=ctx).data,
        })

