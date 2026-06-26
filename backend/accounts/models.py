"""
模块说明：accounts 模块数据模型（ORM）。

本模块负责账号体系相关的持久化数据，涵盖：
- 用户扩展资料（角色、昵称、头像等）
- 邮箱验证码（重置密码、更换绑定邮箱）
- 邮箱变更记录、密码重置记录
- 用户拉黑关系
"""

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    用户扩展资料表。

    与 Django 内置 User 一对一关联，存储平台侧的角色、昵称、联系方式、
    封禁状态及隐私协议同意标记等，是权限判断（visitor / user / admin）的核心依据。
    """

    # 角色枚举：visitor=游客，user=普通用户，admin=管理员
    ROLE_CHOICES = [
        ('user', 'User'),
        ('visitor', 'Visitor'),
        ('admin', 'Admin'),
    ]
    # 账号状态枚举：0=正常，1=封禁
    STATUS_CHOICES = [(0, 'Normal'), (1, 'Banned')]

    # 关联 Django 内置用户，删除用户时级联删除资料
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 用户角色，决定接口访问权限级别
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    # 平台展示昵称，可为空则回退显示用户名
    nickname = models.CharField(max_length=50, blank=True, null=True)
    # 联系电话
    phone = models.CharField(max_length=20, blank=True, null=True)
    # 头像图片地址
    avatar_url = models.CharField(max_length=500, blank=True, null=True)
    # 联系地址
    address = models.CharField(max_length=255, blank=True, null=True)
    # 账号状态，1 表示被封禁后部分功能不可用
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    # 注册时是否已同意隐私协议
    has_privacy_consent = models.BooleanField(default=False)
    # 资料创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 资料最后更新时间
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 对应数据库表名
        db_table = 'user_profile'

    def __str__(self):
        """
        返回可读字符串，便于后台或调试时识别用户。

        返回:
            str: 格式为「用户名 (角色)」
        """
        return f'{self.user.username} ({self.role})'


class UserVerificationCode(models.Model):
    """
    邮箱验证码记录表。

    用于「忘记密码重置」和「更换绑定邮箱」两类场景：
    生成 6 位数字验证码，有效期 15 分钟，使用后标记为已用，防止重复消费。
    """

    # 验证码用途枚举
    PURPOSE_CHOICES = [
        ('reset_password', 'Reset Password'),   # 重置密码
        ('change_email', 'Change Email'),     # 更换绑定邮箱
    ]

    # 接收验证码的邮箱地址
    email = models.CharField(max_length=100)
    # 6 位数字验证码
    code = models.CharField(max_length=10)
    # 验证码用途，与 PURPOSE_CHOICES 对应
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    # 是否已被使用，防止同一验证码重复使用
    is_used = models.BooleanField(default=False)
    # 过期时间，超过后验证码失效
    expires_at = models.DateTimeField()
    # 验证码创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_verification_code'


class UserEmailChangeLog(models.Model):
    """
    邮箱变更历史记录表。

    用户通过验证码确认更换绑定邮箱后，在此留存旧邮箱与新邮箱的对照，
    便于审计与问题追溯。
    """

    # 发生邮箱变更的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_change_logs')
    # 变更前的邮箱
    old_email = models.CharField(max_length=100)
    # 变更后的邮箱
    new_email = models.CharField(max_length=100)
    # 变更发生时间
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_email_change_log'


class UserBlock(models.Model):
    """
    用户拉黑关系表。

    记录「拉黑者 blocker」与「被拉黑者 blocked」之间的单向关系；
    被拉黑后，双方在社区等场景中将互相不可见或受限交互。
    """

    # 发起拉黑的用户
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    # 被拉黑的用户
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    # 拉黑操作时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_block'
        # 同一对用户只能存在一条拉黑记录，防止重复拉黑
        unique_together = [('blocker', 'blocked')]


class UserPasswordResetLog(models.Model):
    """
    密码重置操作日志表。

    用户通过邮箱验证码成功重置密码后写入一条记录，用于安全审计。
    """

    # 重置密码的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_logs')
    # 密码重置完成时间
    reset_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_password_reset_log'
