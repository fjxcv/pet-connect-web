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
    """Haversine 鍏紡璁＄畻涓ょ偣闂磋窛绂伙紙鍏噷锛�"""
    R = 6371
    d_lat = math.radians(float(lat2) - float(lat1))
    d_lon = math.radians(float(lon2) - float(lon1))
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class LostFoundPostViewSet(viewsets.ModelViewSet):
    """鎶ュけ/瀵讳富 CRUD"""
    queryset = LostFoundPost.objects.select_related('publisher').all()
    serializer_class = LostFoundPostSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'nearby']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsActiveUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        post_type = self.request.query_params.get('post_type')
        status_val = self.request.query_params.get('status')
        if post_type:
            qs = qs.filter(post_type=post_type)
        if status_val:
            qs = qs.filter(status=status_val)

        has_reward = self.request.query_params.get('has_reward')
        if has_reward and has_reward.lower() in ('true', '1'):
            qs = qs.filter(reward_amount__gt=0)

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
        lat = serializer.validated_data.get('latitude')
        lon = serializer.validated_data.get('longitude')
        address_text = serializer.validated_data.get('address_text', '')
        # 鏈夊潗鏍囦絾鏃犲湴鍧€鏃讹紝鑷姩閫嗗湴鐞嗙紪鐮�
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
                pass
        serializer.save(publisher=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.publisher != self.request.user and getattr(self.request.user.profile, 'role', None) != 'admin':
            raise PermissionDenied('Not allowed to update this post')
        serializer.save()

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """褰撳墠鐢ㄦ埛鐨勫彂甯冭褰�"""
        qs = self.get_queryset().filter(publisher=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby(self, request):
        """闄勮繎鎼滅储锛氭牴鎹粡绾害鏌ユ壘鎸囧畾鑼冨洿鍐呯殑璁板綍"""
        try:
            lat = float(request.query_params.get('lat', 0))
            lon = float(request.query_params.get('lon', 0))
            radius_km = float(request.query_params.get('radius', 5))
        except (TypeError, ValueError):
            return Response(
                {'detail': '璇锋彁渚涙湁鏁堢殑缁忕含搴﹀弬鏁帮紙lat, lon锛�'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not lat or not lon:
            return Response(
                {'detail': '璇锋彁渚涚粡绾害鍙傛暟'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post_type = request.query_params.get('post_type')
        status_filter = request.query_params.get('status', 'searching')

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
                if distance <= radius_km:
                    data = LostFoundPostSerializer(post).data
                    data['distance_km'] = round(distance, 2)
                    results.append(data)

        results.sort(key=lambda x: x['distance_km'])
        return Response(results)
