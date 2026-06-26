"""
portal 模块：首页轮播图数据模型（ORM）。
【权限】visitor/user 仅读公开；admin 可增删改。
"""

from django.db import models


class PortalCarousel(models.Model):
    """
    功能：首页轮播图（图片+链接+排序+上下线）。
    【权限】visitor/user：list/retrieve 仅 status=1；admin：全部 CRUD
    """
    STATUS_CHOICES = [(0, 'Offline'), (1, 'Online')]
    # 字段说明：0 下线，1 上线（默认上线）
    title = models.CharField(max_length=100, blank=True, null=True)
    # 字段说明：轮播标题（可选）
    image_url = models.CharField(max_length=500)
    # 字段说明：图片 URL（必填）
    link_url = models.CharField(max_length=500, blank=True, null=True)
    # 字段说明：点击跳转链接（可选）
    sort_order = models.IntegerField(default=0)
    # 字段说明：排序权重，数字越小越靠前
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    # 字段说明：上下线状态
    created_at = models.DateTimeField(auto_now_add=True)
    # 字段说明：创建时间
    updated_at = models.DateTimeField(auto_now=True)
    # 字段说明：最后更新时间

    class Meta:
        db_table = 'portal_carousel'
        ordering = ['sort_order', 'id']

