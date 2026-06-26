"""
模块说明：用户认证与个人资料 API 视图。

提供账号注册、JWT 登录、个人资料管理、密码重置、更换绑定邮箱、
公开主页查询及用户拉黑等 HTTP 接口。
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from common.user_block import is_blocked
from community.models import CommunityPost
from community.serializers import CommunityPostSerializer
from lostfound.models import LostFoundPost
from lostfound.serializers import LostFoundPostSerializer
from .models import UserBlock
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .admin_utils import sync_admin_profile_role
from .serializers import (
    EmailChangeConfirmSerializer,
    EmailChangeRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 JWT 登录序列化器。

    在标准 JWT 令牌中额外写入 username、role，
    并在登录成功响应中附带完整用户信息 UserSerializer。
 
    权限：visitor（未登录）可提交用户名密码换取令牌。
    """

    @classmethod
    def get_token(cls, user):
        """
        生成 JWT 访问令牌，并嵌入用户标识与角色。

        参数:
            user (User): 登录成功的用户
        返回:
            Token: 含 username、role 自定义声明的 JWT
        """
        token = super().get_token(user)
        profile = getattr(user, 'profile', None)
        token['username'] = user.username
        # role 用于前端区分 visitor / user / admin 权限展示
        token['role'] = profile.role if profile else 'user'
        return token

    def validate(self, attrs):
        """
        校验用户名密码，同步管理员角色后返回令牌与用户信息。

        参数:
            attrs (dict): 含 username、password 的登录凭据
        返回:
            dict: access、refresh 令牌及 user 完整资料
        """
        data = super().validate(attrs)
        # 若用户为 Django 后台 staff，同步 profile.role 为 admin
        sync_admin_profile_role(self.user)
        data['user'] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT 登录接口视图。

    POST /token/：提交用户名与密码，返回 access、refresh 及用户信息。

    权限：visitor（允许匿名访问）。
    """

    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    账号注册接口。

    POST：提交用户名、邮箱、密码及隐私协议同意，创建新用户。

    权限：visitor（允许匿名注册）。
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        处理注册请求：校验数据、创建用户、返回用户资料。

        参数:
            request: HTTP 请求体含注册字段
        返回:
            Response: 201 + UserSerializer 用户数据
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    """
    当前登录用户个人资料接口。

    GET：查询自己的完整资料（含 profile）。
    PUT：更新邮箱、昵称、手机、头像、地址等可编辑字段。

    权限：user / admin（需已登录；未在类上声明 AllowAny，实际应由路由或全局配置要求认证）。
    """

    def get(self, request):
        """
        获取当前用户资料，并同步管理员角色标记。

        参数:
            request: 当前登录用户 request.user
        返回:
            Response: UserSerializer 完整用户数据
        """
        sync_admin_profile_role(request.user)
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        """
        更新个人资料：仅修改请求体中出现的字段。

        参数:
            request: 请求体可含 email、nickname、phone、avatar_url、address
        返回:
            Response: 更新后的 UserSerializer 数据
        """
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        profile = user.profile
        data = serializer.validated_data
        # 若提交了 email，直接更新 User 表邮箱（非验证码换绑流程）
        if 'email' in data:
            user.email = data['email']
            user.save(update_fields=['email'])
        for field in ['nickname', 'phone', 'avatar_url', 'address']:
            if field in data:
                setattr(profile, field, data[field])
        profile.save()
        return Response(UserSerializer(user).data)


class PasswordResetRequestView(APIView):
    """
    申请重置密码（发送邮箱验证码）接口。

    POST：提交注册邮箱，校验存在后发送 6 位验证码。

    权限：visitor（忘记密码场景，无需登录）。
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        向已注册邮箱发送密码重置验证码。

        参数:
            request: 请求体含 email
        返回:
            Response: 发送成功提示
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification code sent'})


class PasswordResetConfirmView(APIView):
    """
    确认重置密码（验证码 + 新密码）接口。

    POST：提交邮箱、验证码、新密码，校验通过后更新密码。

    权限：visitor（无需登录）。
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        校验验证码并设置新密码。

        参数:
            request: 请求体含 email、code、new_password
        返回:
            Response: 重置成功提示
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset successful'})


class EmailChangeRequestView(APIView):
    """
    申请更换绑定邮箱（向新邮箱发验证码）接口。

    POST：提交 new_email，校验未被占用后向新邮箱发码。

    权限：user / admin（需已登录，使用 request.user）。
    """

    def post(self, request):
        """
        向新邮箱发送换绑验证码。

        参数:
            request: 请求体含 new_email
        返回:
            Response: 验证码已发送至新邮箱
        """
        serializer = EmailChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response({'detail': 'Verification code sent to new email'})


class EmailChangeConfirmView(APIView):
    """
    确认更换绑定邮箱（验证码确认）接口。

    POST：提交 new_email、code，校验通过后更新当前用户邮箱。

    权限：user / admin（需已登录）。
    """

    def post(self, request):
        """
        校验换绑验证码并更新用户邮箱。

        参数:
            request: 请求体含 new_email、code
        返回:
            Response: 更新后的 UserSerializer 用户数据
        """
        serializer = EmailChangeConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response(UserSerializer(request.user).data)


User = get_user_model()


class PublicUserProfileView(APIView):
    """
    用户公开主页接口。

    GET：根据用户 ID 返回昵称、头像、角色、是否封禁、
    是否已被当前用户拉黑，以及该用户发布的社区帖、养宠经验帖、寻宠帖摘要。

    权限：
    - visitor / user / admin 均可访问公开主页；
    - 若当前用户与对方存在拉黑关系，返回 403；
    - 被封禁用户不展示其帖子列表。
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        """
        查询指定用户的公开主页信息。

        参数:
            request: 当前请求（可未登录）
            pk (int): 目标用户主键
        返回:
            Response: 公开资料及最多 20 条各类帖子摘要
        """
        user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
        profile = getattr(user, 'profile', None)
        is_banned = bool(profile and profile.status == 1)
        is_blocked_by_me = False
        # 已登录且非本人：查询当前用户是否已拉黑对方
        if request.user.is_authenticated and request.user.pk != user.pk:
            is_blocked_by_me = UserBlock.objects.filter(blocker=request.user, blocked=user).exists()
        # 双向拉黑校验：任一方拉黑则不可查看对方主页
        if request.user.is_authenticated and is_blocked(request.user, user):
            return Response({'detail': 'blocked_by_user'}, status=status.HTTP_403_FORBIDDEN)
        posts = CommunityPost.objects.none()
        pet_posts = CommunityPost.objects.none()
        lost_posts = LostFoundPost.objects.none()
        # 未封禁用户才展示其历史发帖
        if not is_banned:
            posts = CommunityPost.objects.filter(author=user, is_deleted=False).order_by('-created_at')[:20]
            pet_posts = CommunityPost.objects.filter(
                author=user, is_deleted=False, category='pet_experience',
            ).order_by('-created_at')[:20]
            lost_posts = LostFoundPost.objects.filter(
                publisher=user, status='searching',
            ).order_by('-created_at')[:20]
        ctx = {'request': request}
        return Response({
            'id': user.id,
            'username': user.username,
            'nickname': profile.nickname if profile else None,
            'avatar_url': profile.avatar_url if profile else None,
            'role': profile.role if profile else 'user',
            'is_banned': is_banned,
            'is_blocked_by_me': is_blocked_by_me,
            'joined_at': profile.created_at if profile else None,
            'community_posts': CommunityPostSerializer(posts, many=True, context=ctx).data,
            'pet_experience_posts': CommunityPostSerializer(pet_posts, many=True, context=ctx).data,
            'lost_found_posts': LostFoundPostSerializer(lost_posts, many=True).data,
        })


class UserBlockView(APIView):
    """
    用户拉黑 / 取消拉黑接口。

    POST：拉黑指定用户（不可拉黑自己）。
    DELETE：取消对指定用户的拉黑。

    权限：user / admin（需已登录，visitor 不可操作）。
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """
        拉黑指定用户。

        参数:
            request: 当前登录用户为拉黑发起方
            pk (int): 被拉黑用户 ID
        返回:
            Response: 成功或 400（不能拉黑自己）
        """
        if request.user.pk == pk:
            return Response({'detail': 'Cannot block yourself'}, status=status.HTTP_400_BAD_REQUEST)
        blocked_user = get_object_or_404(User, pk=pk)
        UserBlock.objects.get_or_create(blocker=request.user, blocked=blocked_user)
        return Response({'detail': 'User blocked'})

    def delete(self, request, pk):
        """
        取消拉黑指定用户。

        参数:
            request: 当前登录用户
            pk (int): 被取消拉黑的用户 ID
        返回:
            Response: 取消拉黑成功提示
        """
        UserBlock.objects.filter(blocker=request.user, blocked_id=pk).delete()
        return Response({'detail': 'User unblocked'})
