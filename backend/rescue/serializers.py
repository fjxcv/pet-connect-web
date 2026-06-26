"""
模块说明：rescue 模块序列化器。

负责救助案例、状态日志、阶段记录的校验与 JSON 转换，
以及救助编号自动生成（RES + 日期 + 流水号）。
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Max
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import RescueCase, RescueStageRecord, RescueStatusLog


def _round_coordinate(value):
    """
    将坐标值四舍五入到 6 位小数，统一 GPS 精度。

    参数:
        value: 原始纬度或经度
    返回:
        Decimal | None: 规范化后的坐标，空值返回 None
    """
    if value is None or value == '':
        return None
    return Decimal(str(value)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


class CoordinateField(serializers.DecimalField):
    """
    经纬度专用字段。

    自动限制 9 位总长度、6 位小数，写入前经 _round_coordinate 规范化。
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('max_digits', 9)
        kwargs.setdefault('decimal_places', 6)
        kwargs.setdefault('required', False)
        kwargs.setdefault('allow_null', True)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
        反序列化坐标：空值透传，否则四舍五入后校验。

        参数:
            data: 前端传入的 lat/lng
        返回:
            Decimal | None: 规范化坐标
        """
        if data in (None, ''):
            return None
        return super().to_internal_value(_round_coordinate(data))


class RescueStatusLogSerializer(serializers.ModelSerializer):
    """
    救助状态变更日志序列化器。

    用于嵌套在救助案例详情中展示状态时间线。

    权限：visitor / user / admin 均可只读查看。
    """

    operator = UserSerializer(read_only=True)

    class Meta:
        model = RescueStatusLog
        fields = '__all__'


class RescueCaseSerializer(serializers.ModelSerializer):
    """
    救助案例序列化器。

    用于上报救助、列表/详情展示；
    rescue_no 由服务端 generate_rescue_no 自动生成，reporter/helpers 由视图写入。

    权限：
    - visitor / user：只读 list/retrieve
    - user：可 create（上报救助，含 GPS 与 discover_address）
    - admin：可 update/destroy
    """

    reporter = UserSerializer(read_only=True)
    helpers = UserSerializer(many=True, read_only=True)
    # 状态变更时间线，按 created_at 正序
    status_logs = RescueStatusLogSerializer(many=True, read_only=True)
    discover_latitude = CoordinateField()
    discover_longitude = CoordinateField()

    class Meta:
        model = RescueCase
        fields = '__all__'
        read_only_fields = ['rescue_no', 'reporter', 'helpers', 'help_date', 'created_at', 'updated_at']

    def validate_discover_address(self, value):
        """
        校验发现地点文字地址非空。

        说明：前端通常通过 GPS + 高德逆地理编码 API 自动填充此字段，
        用户也可手动补充或修正。

        参数:
            value (str): 发现地址
        返回:
            str: strip 后的地址
        异常:
            ValidationError: 为空时
        """
        text = (value or '').strip()
        if not text:
            raise serializers.ValidationError('\u8bf7\u586b\u5199\u53d1\u73b0\u5730\u70b9\u6216\u9644\u8fd1\u5730\u6807\u3002')
        return text

    def validate_nickname(self, value):
        """
        校验上报人昵称非空。

        参数:
            value (str): 昵称
        返回:
            str: strip 后的昵称
        异常:
            ValidationError: 为空时
        """
        text = (value or '').strip()
        if not text:
            raise serializers.ValidationError('\u8bf7\u586b\u5199\u60a8\u7684\u6635\u79f0\u3002')
        return text

    def validate_contact(self, value):
        """
        校验联系方式非空且格式合理。

        说明：响应救助（help）时，前端弹窗展示此联系方式供救助人联系上报者。

        参数:
            value (str): 手机号或微信号等
        返回:
            str: strip 后的联系方式
        异常:
            ValidationError: 为空或长度不足 5 时
        """
        text = (value or '').strip()
        if not text:
            raise serializers.ValidationError('\u8bf7\u586b\u5199\u60a8\u7684\u8054\u7cfb\u65b9\u5f0f\u3002')
        if len(text) < 5:
            raise serializers.ValidationError('\u8054\u7cfb\u65b9\u5f0f\u683c\u5f0f\u4e0d\u6b63\u786e\uff0c\u8bf7\u586b\u5199\u624b\u673a\u53f7\u6216\u5fae\u4fe1\u53f7\u3002')
        return text


class RescueStageRecordSerializer(serializers.ModelSerializer):
    """
    救助阶段记录序列化器。

    救助人或管理员填写各阶段进展（治疗、喂养、康复等）。

    权限：救助响应者（helpers）或 admin 可创建；所有人可读 GET 列表。
    """

    operator = UserSerializer(read_only=True)

    class Meta:
        model = RescueStageRecord
        fields = ['id', 'rescue_case', 'content', 'operator', 'created_at']
        read_only_fields = ['rescue_case', 'operator', 'created_at']


def generate_rescue_no():
    """
    自动生成唯一救助编号。

    格式：RES + YYYYMMDD + 3 位当日流水号，例如 RES20260614001。
    同一天多次上报时流水号递增。

    返回:
        str: 新的 rescue_no
    """
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'RES{today}'
    last = RescueCase.objects.filter(rescue_no__startswith=prefix).aggregate(Max('rescue_no'))['rescue_no__max']
    # 格式 RES20260614001（年月日 + 3位流水号）
    seq = int(last[-3:]) + 1 if last else 1
    return f'{prefix}{seq:03d}'
