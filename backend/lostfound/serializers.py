"""
lostfound 序列化器：坐标精度处理 + 电话脱敏（本人/admin 可见）。
"""

from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import LostFoundPost


def _round_coordinate(value):
    """
    功能：坐标保留 6 位小数（Haversine 需要）。
    """
    if value is None or value == '':
        return None
    return Decimal(str(value)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


class CoordinateField(serializers.DecimalField):
    """
    功能：自定义坐标字段，自动 6 位小数 + 可空。
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('max_digits', 9)
        kwargs.setdefault('decimal_places', 6)
        kwargs.setdefault('required', False)
        kwargs.setdefault('allow_null', True)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data in (None, ''):
            return None
        return super().to_internal_value(_round_coordinate(data))


class LostFoundPostSerializer(serializers.ModelSerializer):
    """
    功能：报失寻主序列化器。
    字段：publisher 只读；latitude/longitude 自动精度；contact_phone_display 脱敏。
    【权限】visitor 读脱敏；user 读本人/发布者；admin 读完整
    """
    publisher = UserSerializer(read_only=True)
    latitude = CoordinateField()
    longitude = CoordinateField()
    contact_phone_display = serializers.SerializerMethodField()

    class Meta:
        model = LostFoundPost
        fields = '__all__'
        read_only_fields = ['publisher', 'created_at', 'updated_at', 'contact_phone_display']

    def get_contact_phone_display(self, obj):
        """
        功能：电话脱敏逻辑（本人或 admin 可见完整，其余 138****1234）。
        【权限】publisher/admin 完整；visitor/user 脱敏
        """
        request = self.context.get('request')
        phone = obj.contact_phone
        if not phone:
            return None
        if request and request.user.is_authenticated:
            if request.user == obj.publisher:
                return phone
            if getattr(request.user.profile, 'role', None) == 'admin':
                return phone
        phone_str = str(phone).strip()
        if len(phone_str) >= 7:
            return phone_str[:3] + '****' + phone_str[-4:]
        return phone_str[:3] + '****'

    def validate_photo_urls(self, value):
        """
        功能：至少上传 1 张照片。
        """
        if not value or not isinstance(value, list) or len(value) < 1:
            raise serializers.ValidationError('请至少上传 1 张宠物照片')
        return value

    def validate_address_text(self, value):
        text = (value or '').strip()
        if not text:
            return ''
        return text
