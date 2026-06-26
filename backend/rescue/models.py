"""
模块说明：rescue 模块数据模型（ORM）。

本模块负责流浪动物救助案例相关的持久化数据，涵盖：
- 救助案例上报（GPS 定位 + 发现地址，前端通过高德逆地理编码获取地址文字）
- 救助编号自动生成（RES + 日期 + 流水号）
- 救助状态机流转与时间线日志
- 救助响应（help）与阶段记录
"""

from django.contrib.auth.models import User
from django.db import models


class RescueCase(models.Model):
    """
    救助案例表。

    用户上报发现的流浪动物，携带 GPS 坐标与发现地址；
    状态按流程单向推进：待救助 → 医疗中 → 恢复中 → 待领养 → 救助成功。
    其他用户可响应救助（help），首次响应时自动推进到「医疗中」。
    """

    # 救助状态枚举（状态机节点）
    STATUS_CHOICES = [
        ('pending_rescue', 'Pending Rescue'),     # 待救助
        ('in_medical', 'In Medical'),             # 医疗中
        ('recovering', 'Recovering'),             # 恢复中
        ('awaiting_adoption', 'Awaiting Adoption'),  # 待领养
        ('rescued', 'Rescued'),                   # 救助成功
        ('abandoned', 'Abandoned'),               # 已放弃
    ]
    # 体型枚举
    SIZE_CHOICES = [
        ('small', '\u5c0f\u578b'),
        ('medium', '\u4e2d\u578b'),
        ('large', '\u5927\u578b'),
    ]
    # 健康状况枚举
    HEALTH_CHOICES = [
        ('healthy', '\u5065\u5eb7'),
        ('minor_injury', '\u8f7b\u5fae\u4f24\u75c5'),
        ('severe_injury', '\u4e25\u91cd\u4f24\u75c5'),
    ]

    # 救助编号，格式 RES20260614001（RES + 年月日 + 3位流水号），唯一
    rescue_no = models.CharField(max_length=32, unique=True)
    # 上报人（发现者）
    reporter = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='rescue_cases')
    # 响应救助的用户（可多人）
    helpers = models.ManyToManyField(User, related_name='helped_cases', blank=True)
    # 救助行动开始日期（首次被响应时记录）
    help_date = models.DateTimeField(null=True, blank=True)
    # 上报人填写的昵称（允许代他人上报，不使用 profile 自动填充）
    nickname = models.CharField(max_length=50, default='', blank=True)
    # 上报人联系方式（响应救助时在弹窗中展示）
    contact = models.CharField(max_length=100, default='', blank=True)
    # 发现地点纬度（GPS 定位，前端上报）
    discover_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # 发现地点经度
    discover_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # 发现地点文字地址（前端通过高德逆地理编码 API 由坐标转换得到）
    discover_address = models.CharField(max_length=255)
    # 动物体型
    size_category = models.CharField(max_length=20, choices=SIZE_CHOICES, default='', blank=True)
    # 健康状况分类
    health_status = models.CharField(max_length=20, choices=HEALTH_CHOICES, default='', blank=True)
    # 是否受伤
    is_injured = models.BooleanField(default=False)
    # 是否怕人
    afraid_of_people = models.BooleanField(default=False)
    # 外观描述（毛色、特征等）
    appearance = models.TextField(blank=True, null=True)
    # 健康备注
    health_note = models.TextField(blank=True, null=True)
    # 现场照片 URL 列表，JSON 数组
    photo_urls = models.JSONField(default=list, blank=True)
    # 当前救助状态
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_rescue')
    # 案例创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 案例最后更新时间
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rescue_case'
        ordering = ['-created_at']


class RescueStatusLog(models.Model):
    """
    救助状态变更日志表（时间线）。

    每次状态流转（含首次上报、响应救助、手动推进）均写入一条记录，
    形成完整的状态时间线，供前端展示救助进度。
    """

    # 所属救助案例
    rescue_case = models.ForeignKey(RescueCase, on_delete=models.CASCADE, related_name='status_logs')
    # 变更前状态，首次上报时为 None
    from_status = models.CharField(max_length=20, blank=True, null=True)
    # 变更后状态
    to_status = models.CharField(max_length=20)
    # 操作人（上报人、响应者或管理员）
    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='rescue_status_operations')
    # 状态变更备注（手动推进时必填，如诊断结果、治疗方案）
    remark = models.TextField(blank=True, null=True)
    # 记录创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rescue_status_log'
        ordering = ['created_at']


class RescueStageRecord(models.Model):
    """
    救助各阶段详细记录表。

    救助人或管理员可在医疗中、恢复中等阶段多次填写进展记录，
    与状态日志互补：状态日志记录节点切换，本表记录阶段内的详细内容。
    """

    # 所属救助案例
    rescue_case = models.ForeignKey(RescueCase, on_delete=models.CASCADE, related_name='stage_records')
    # 阶段记录正文（治疗进展、喂养情况等）
    content = models.TextField()
    # 填写人
    operator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='rescue_stage_records')
    # 记录创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rescue_stage_record'
        ordering = ['-created_at']
