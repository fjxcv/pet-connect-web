"""
portal 序列化器：轮播图序列化。
"""

from rest_framework import serializers

from .models import PortalCarousel


class PortalCarouselSerializer(serializers.ModelSerializer):
    """轮播图序列化器（字段全暴露）。【权限】admin 写，visitor 读公开"""

    class Meta:
        model = PortalCarousel
        fields = '__all__'

