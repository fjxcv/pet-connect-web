"""
lostfound 模块：报失/寻主帖子模型（支持坐标、报酬、状态流转）。
【权限】visitor 读公开；user 可发布/修改本人；admin 全部
"""

from django.contrib.auth.models import User
from django.db import models


class LostFoundPost(models.Model):
    """
    功能：报失（lost）/寻主（found）帖子。
    状态流转：searching → found / cancelled。
    【权限】visitor 读；user 发布/修改本人；admin 全部
    """
    POST_TYPE_CHOICES = [('lost', 'Lost'), ('found', 'Found')]
    # 字段说明：帖子类型（lost 报失 / found 寻主）
    STATUS_CHOICES = [
        ('searching', 'Searching'),
        ('found', 'Found'),
        ('cancelled', 'Cancelled'),
    ]
    # 字段说明：searching 寻找中、found 已找到、cancelled 已取消
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_found_posts')
    # 字段说明：发布者（登录用户）
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    # 字段说明：类型
    pet_species = models.CharField(max_length=50)
    # 字段说明：宠物种类（猫/狗/...）
    features = models.TextField()
    # 字段说明：特征描述
    photo_urls = models.JSONField(default=list, blank=True)
    # 字段说明：照片 URL 列表（至少 1 张）
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # 字段说明：纬度（6 位小数）
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # 字段说明：经度（6 位小数）
    address_text = models.CharField(max_length=255)
    # 字段说明：地址文本（必填）
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # 字段说明：悬赏金额（默认 0）
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    # 字段说明：联系电话（本人/ admin 可见，其余脱敏）
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='searching')
    # 字段说明：状态
    created_at = models.DateTimeField(auto_now_add=True)
    # 字段说明：创建时间
    updated_at = models.DateTimeField(auto_now=True)
    # 字段说明：最后更新时间

    class Meta:
        db_table = 'lost_found_post'
        ordering = ['-created_at']
