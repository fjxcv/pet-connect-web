"""
lostfound 视图：报失寻主 CRUD + 附近搜索（Haversine 算法）。
"""

import math
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from common.permissions import IsActiveUser
from .models import LostFoundPost
from .serializers import LostFoundPostSerializer


def _haversine_distance(lat1, lon1, lat2, lon2):
    """
    功能：Haversine 公式计算两点球面距离（单位 km）。
    用于附近搜索。
    """
    R = 6371
    d_lat = math.radians(float(lat2) - float(lat1))
    d_lon = math.radians(float(lon2) - float(lon1))
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # 返回地球表面两点之间的大圆距离，适合用于近距离搜索
    return R * c


class LostFoundPostViewSet(viewsets.ModelViewSet):
    """
    功能：报失寻主 CRUD + my_posts + nearby。
    【权限】list/retrieve/nearby：visitor；其余：user（未封禁）；更新本人或 admin
    """
    queryset = LostFoundPost.objects.select_related('publisher').all()
    serializer_class = LostFoundPostSerializer

    def get_permissions(self):
        # 公开接口：列表、详情、附近搜索对任何人开放
        # 受限接口：创建、更新、删除仅对登录且未封禁用户开放
        if self.action in ['list', 'retrieve', 'nearby']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsActiveUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        # 解析查询参数并按条件过滤
        post_type = self.request.query_params.get('post_type')
        status_val = self.request.query_params.get('status')
        if post_type:
            qs = qs.filter(post_type=post_type)
        if status_val:
            qs = qs.filter(status=status_val)
        # 仅返回有奖励的帖子
        has_reward = self.request.query_params.get('has_reward')
        if has_reward and has_reward.lower() in ('true', '1'):
            qs = qs.filter(reward_amount__gt=0)
        # 支持关键字搜索：宠物品种、特征、地址说明
        search_q = (self.request.query_params.get('q') or self.request.query_params.get('search') or '').strip()
        if search_q:
            qs = qs.filter(
                Q(pet_species__icontains=search_q)
                | Q(features__icontains=search_q)
                | Q(address_text__icontains=search_q)
            )
        species_kw = (self.request.query_params.get('species_keyword') or '').strip()
        if species_kw:
            qs = qs.filter(pet_species__icontains=species_kw)
        return qs

    def perform_create(self, serializer):
        """
        功能：创建时若有坐标无地址，调用 Nominatim 反向地理编码自动填充 address_text。
        【权限】user
        """
        lat = serializer.validated_data.get('latitude')
        lon = serializer.validated_data.get('longitude')
        address_text = serializer.validated_data.get('address_text', '')
        # 如果请求提供了经纬度但没有地址描述，则尝试使用公开地图服务补全地址
        if lat is not None and lon is not None and not address_text:
            try:
                import requests
                headers = {'User-Agent': 'PetConnectWeb/1.0 (pet-connect-app)'}
                url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=zh'
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    display_name = data.get('display_name', '')
                    if display_name:
                        serializer.validated_data['address_text'] = display_name
            except Exception:
                # 反向地理编码失败时不阻止发布，仅忽略额外地址补全
                pass
        serializer.save(publisher=self.request.user)

    def perform_update(self, serializer):
        """
        功能：更新权限校验（仅发布者或 admin）。
        【权限】publisher 或 admin
        """
        instance = self.get_object()
        # 仅允许帖子发布者本人或 admin 角色更新数据
        if instance.publisher != self.request.user and getattr(self.request.user.profile, 'role', None) != 'admin':
            raise PermissionDenied('Not allowed to update this post')
        serializer.save()

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """
        功能：我的发布列表。
        【权限】user（本人）
        """
        # 返回当前登录用户发布的所有报失寻主帖子
        qs = self.get_queryset().filter(publisher=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby(self, request):
        """
        功能：附近搜索（Haversine 半径过滤 + 距离排序）。
        参数：lat, lon, radius（默认 5km），post_type, status
        【权限】visitor
        """
        try:
            lat = float(request.query_params.get('lat', 0))
            lon = float(request.query_params.get('lon', 0))
            radius_km = float(request.query_params.get('radius', 5))
        except (TypeError, ValueError):
            return Response(
                {'detail': '参数错误：请提供合法的 lat, lon'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # lat/lon 必填，否则无法进行地理距离计算
        if not lat or not lon:
            return Response(
                {'detail': '参数错误：lat 和 lon 不能为空'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        post_type = request.query_params.get('post_type')
        status_filter = request.query_params.get('status', 'searching')
        # 仅查询具有经纬度数据的帖子，避免空值导致距离计算异常
        qs = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False,
        )
        if post_type:
            qs = qs.filter(post_type=post_type)
        if status_filter:
            qs = qs.filter(status=status_filter)
        results = []
        for post in qs:
            if post.latitude and post.longitude:
                distance = _haversine_distance(lat, lon, float(post.latitude), float(post.longitude))
                # 只返回在指定半径范围内的帖子
                if distance <= radius_km:
                    data = LostFoundPostSerializer(post).data
                    data['distance_km'] = round(distance, 2)
                    results.append(data)
        # 按距离升序排列，最近的结果优先
        results.sort(key=lambda x: x['distance_km'])
        return Response(results)
