"""
模块说明：pets 模块数据模型（ORM）。

本模块负责宠物档案与领养流程相关的持久化数据，涵盖：
- 宠物档案（种类、性别、体型、地区、年龄、领养状态）
- 领养申请三步流程（申请 → 问卷 → 附件）
- 管理员线上审核与线下核验记录
"""

from django.contrib.auth.models import User
from django.db import models
from rescue.models import RescueCase


class PetProfile(models.Model):
    """
    宠物档案表。

    展示待领养宠物的基本信息与地理位置，可关联救助案例（rescue_case）；
    支持多维度筛选（种类/性别/体型/地区/年龄）及附近搜索（Haversine 距离计算）。
    """

    # 领养状态枚举：available=可领养，pending=申请中，adopted=已领养
    ADOPTION_STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('adopted', 'Adopted'),
    ]
    # 体型分类枚举
    SIZE_CATEGORY_CHOICES = [
        ('small', '\u5c0f\u578b'),
        ('medium', '\u4e2d\u578b'),
        ('large', '\u5927\u578b'),
    ]

    # 关联的救助案例，救助成功后转为宠物档案；删除案例时置空
    rescue_case = models.ForeignKey(
        RescueCase, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets'
    )
    # 宠物名称
    name = models.CharField(max_length=100)
    # 物种（如猫、狗）
    species = models.CharField(max_length=50)
    # 品种，可为空
    breed = models.CharField(max_length=100, blank=True, null=True)
    # 年龄（月），用于 age_min/age_max 筛选
    age_months = models.IntegerField(blank=True, null=True)
    # 性别（如 male/female）
    gender = models.CharField(max_length=10, blank=True, null=True)
    # 体型分类：small/medium/large
    size_category = models.CharField(max_length=10, choices=SIZE_CATEGORY_CHOICES, blank=True, null=True)
    # 健康状况描述
    health_status = models.CharField(max_length=100, blank=True, null=True)
    # 宠物介绍正文
    description = models.TextField(blank=True, null=True)
    # 主图 URL
    photo_url = models.CharField(max_length=500, blank=True, null=True)
    # 国家，用于地区筛选
    country = models.CharField(max_length=50, blank=True, null=True)
    # 省/州
    province = models.CharField(max_length=50, blank=True, null=True)
    # 城市
    city = models.CharField(max_length=50, blank=True, null=True)
    # 区/县
    district = models.CharField(max_length=50, blank=True, null=True)
    # 详细位置文字描述
    location_text = models.CharField(max_length=255, blank=True, null=True)
    # 纬度，附近搜索时使用；为空则回退 rescue_case 坐标
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    # 经度
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    # 当前领养状态
    adoption_status = models.CharField(max_length=20, choices=ADOPTION_STATUS_CHOICES, default='available')
    # 是否对外公开展示，已领养宠物通常设为 False
    is_public = models.BooleanField(default=True)
    # 档案创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 档案最后更新时间
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pet_profile'
        ordering = ['-created_at']


class AdoptApplication(models.Model):
    """
    领养申请表。

    用户三步提交流程：
    1. 创建申请（本表，online_status=pending，宠物状态改为 pending）
    2. 填写问卷（AdoptQuestionnaire，answers_json 存储 JSON）
    3. 上传证明材料（AdoptAttachment）

    管理员线上审核：通过 / 拒绝 / 需补充材料（need_material）。
    """

    # 线上审核状态枚举
    ONLINE_STATUS_CHOICES = [
        ('pending', 'Pending'),           # 待审核
        ('approved', 'Approved'),         # 已通过
        ('rejected', 'Rejected'),         # 已拒绝
        ('need_material', 'Need Material'),  # 需补充材料
    ]

    # 申请人
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adopt_applications')
    # 目标宠物，RESTRICT 防止有申请时误删宠物
    pet = models.ForeignKey(PetProfile, on_delete=models.RESTRICT, related_name='applications')
    # 线上审核状态
    online_status = models.CharField(max_length=20, choices=ONLINE_STATUS_CHOICES, default='pending')
    # 管理员审核意见（拒绝时必填）
    audit_opinion = models.TextField(blank=True, null=True)
    # 审核管理员
    auditor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audited_applications'
    )
    # 审核完成时间
    audited_at = models.DateTimeField(blank=True, null=True)
    # 申请人附言
    message = models.TextField(blank=True, null=True)
    # 申请创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 申请最后更新时间
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'adopt_application'
        ordering = ['-created_at']


class AdoptQuestionnaire(models.Model):
    """
    领养问卷表。

    与申请一对一关联，answers_json 以 JSON 格式存储问卷全部答案，
    便于灵活扩展题目而不改表结构。
    """

    # 所属领养申请，一对一
    application = models.OneToOneField(
        AdoptApplication, on_delete=models.CASCADE, related_name='questionnaire'
    )
    # 问卷答案 JSON，结构由前端约定
    answers_json = models.JSONField()
    # 问卷提交时间
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'adopt_questionnaire'


class AdoptAttachment(models.Model):
    """
    领养申请附件表。

    存储用户上传的证明材料元数据（身份证、收入证明等），
    实际文件 URL 由前端上传后传入。
    """

    # 所属领养申请，一条申请可有多份附件
    application = models.ForeignKey(AdoptApplication, on_delete=models.CASCADE, related_name='attachments')
    # 文件类型标识（如 id_card、income_proof）
    file_type = models.CharField(max_length=30)
    # 文件访问 URL
    file_url = models.CharField(max_length=500)
    # 文件大小（字节）
    file_size = models.IntegerField()
    # 上传时间
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'adopt_attachment'


class AdoptOfflineVerify(models.Model):
    """
    线下核验记录表。

    线上审核通过后，管理员安排线下见面核验，
    记录核验结果：scheduled（待核验）/ passed（通过）/ failed（失败）。
    """

    # 线下核验状态枚举
    VERIFY_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),  # 已安排待核验
        ('passed', 'Passed'),      # 核验通过
        ('failed', 'Failed'),      # 核验失败
    ]

    # 所属领养申请，一对一
    application = models.OneToOneField(
        AdoptApplication, on_delete=models.CASCADE, related_name='offline_verify'
    )
    # 核验结果状态
    verify_status = models.CharField(max_length=20, choices=VERIFY_STATUS_CHOICES, default='scheduled')
    # 核验备注（失败时必填原因）
    verify_note = models.TextField(blank=True, null=True)
    # 执行核验的管理员
    verifier = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='offline_verifications'
    )
    # 核验完成时间
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'adopt_offline_verify'
