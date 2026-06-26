"""
模块说明：智能后台管理与 AI 辅助 API 视图。

包含：运营看板、用户管理、内容审核、平台配置、
AI 品种识别 / 领养文案 / 智能问答三条链路、AI 调用日志查询与用量统计。
"""

import json

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from accounts.serializers import UserSerializer
from cms.models import CmsArticle
from community.models import CommunityPost
from common.ai_quota import AiQuotaExceededError, check_ai_quota, get_ai_usage_stats, log_quota_exceeded
from common.breed_classifier import BreedModelNotReadyError
from common.breed_detect import detect_pet_breed
from common.image_loader import ImageLoadError
from common.llm_client import LLMNotConfiguredError, LLMRequestError, chat
from common.permissions import IsAdminRole
from common.utils import get_client_ip, write_operation_log
from lostfound.models import LostFoundPost
from pets.models import AdoptApplication, PetProfile
from rescue.models import RescueCase
from .moderation_apply import apply_moderation
from .models import AiInvocationLog, ContentModeration, OperationLog, PlatformConfig
from .serializers import (
    AiInvocationLogSerializer,
    ContentModerationSerializer,
    OperationLogSerializer,
    PlatformConfigSerializer,
)

User = get_user_model()


class AdminDashboardView(APIView):
    """运营数据看板：聚合全站 KPI，仅管理员可读。
    【权限】visitor：不可访问；user：不可访问；admin：可访问。
    """
    permission_classes = [IsAdminRole]

    def get(self, request):
        """返回用户、宠物、申请、救助、社区、CMS、报失及领养状态分布。
        参数：request - DRF 请求对象。
        返回：Response，JSON 含各模块计数。
        【权限】仅 admin。
        """
        return Response({
            'users': User.objects.count(),
            'pets': PetProfile.objects.count(),
            'adopt_applications': AdoptApplication.objects.count(),
            'rescue_cases': RescueCase.objects.count(),
            'community_posts': CommunityPost.objects.filter(is_deleted=False).count(),
            'cms_articles': CmsArticle.objects.filter(status=1).count(),
            'lost_found_posts': LostFoundPost.objects.count(),
            'adopt_by_status': list(
                AdoptApplication.objects.values('online_status').annotate(count=Count('id'))
            ),
        })


class AdminUserViewSet(viewsets.GenericViewSet):
    """后台用户管理：列表筛选、封禁与角色调整。
    【权限】visitor：不可访问；user：不可访问；admin：可访问。
    """
    queryset = User.objects.select_related('profile').all()
    permission_classes = [IsAdminRole]

    def list(self, request):
        """按 role/status 筛选用户列表，最多返回 100 条。
        参数：request - 可带 query 参数 role、status。
        返回：Response，用户列表 JSON。
        【权限】仅 admin。
        """
        users = self.get_queryset()
        role = request.query_params.get('role')
        status_val = request.query_params.get('status')
        # 分支：按角色筛选
        if role:
            users = users.filter(profile__role=role)
        # 分支：按封禁状态筛选（0 正常，1 封禁）
        if status_val is not None:
            users = users.filter(profile__status=int(status_val))
        return Response(UserSerializer(users[:100], many=True).data)

    def partial_update(self, request, pk=None):
        """更新用户封禁状态或角色，并同步 is_staff 与操作日志。
        参数：request - 请求体可含 status、role；pk - 目标用户 ID。
        返回：Response，更新后的用户信息。
        【权限】仅 admin。
        """
        user = User.objects.select_related('profile').get(pk=pk)
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'user', 'has_privacy_consent': True},
        )
        # 分支：更新封禁状态
        if 'status' in request.data:
            profile.status = int(request.data['status'])
        # 分支：更新角色并同步 Django is_staff
        if 'role' in request.data:
            profile.role = request.data['role']
            # 设为 admin 时开启 staff 权限（超级用户除外）
            if request.data['role'] == 'admin' and not user.is_superuser:
                user.is_staff = True
                user.save(update_fields=['is_staff'])
            # 取消 admin 时关闭 staff 权限
            elif request.data['role'] != 'admin' and not user.is_superuser:
                user.is_staff = False
                user.save(update_fields=['is_staff'])
        profile.save()
        user.refresh_from_db()
        write_operation_log(
            request.user, 'admin', 'user_update',
            f'Updated user {user.username}',
            'user', user.id, get_client_ip(request),
        )
        return Response(UserSerializer(user).data)


class AdminModerationViewSet(viewsets.ModelViewSet):
    """内容审核：写入审核记录并联动业务表。
    【权限】visitor：不可访问；user：不可访问；admin：可创建与查询。
    """
    queryset = ContentModeration.objects.select_related('operator').all()
    serializer_class = ContentModerationSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        """先写入审核记录，再联动业务表；失败则回滚审核行。
        参数：serializer - 已通过校验的序列化器。
        返回：无。
        【权限】仅 admin。
        """
        mod = serializer.save(operator=self.request.user)
        try:
            apply_moderation(mod.content_type, mod.content_id, mod.action)
        except ValueError as exc:
            # 分支：业务实体不存在或动作非法时回滚审核记录
            mod.delete()  # 业务实体不存在或动作非法时回滚
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': str(exc)}) from exc
        write_operation_log(
            self.request.user, 'moderation', mod.action,
            f'{mod.content_type}#{mod.content_id}: {mod.action}',
            mod.content_type, mod.content_id, get_client_ip(self.request),
        )


class AdminConfigViewSet(viewsets.ModelViewSet):
    """平台配置维护（含 AI 配额等）。
    【权限】visitor：不可访问；user：不可访问；admin：可增删改查。
    """
    queryset = PlatformConfig.objects.all()
    serializer_class = PlatformConfigSerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'config_key'


class AdminOperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作审计日志只读查询。
    【权限】visitor：不可访问；user：不可访问；admin：只读查询。
    """
    queryset = OperationLog.objects.select_related('operator').all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAdminRole]


def _ai_error_response(exc):
    """将 LLM 异常映射为 503（未配置）或 502（上游失败）。
    参数：exc - LLM 相关异常实例。
    返回：DRF Response 错误响应。
    """
    # 分支：未配置 LLM 环境变量
    if isinstance(exc, LLMNotConfiguredError):
        return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


def _ai_quota_response(exc, user, feature_type, request_meta=''):
    """配额超限时记失败日志并返回 HTTP 429。
    参数：exc - 配额异常；user - 当前用户；feature_type - AI 功能类型；request_meta - 请求摘要。
    返回：DRF Response，状态码 429。
    """
    log_quota_exceeded(user, feature_type, request_meta)
    return Response({'detail': str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)


class AiBreedDetectView(APIView):
    """AI 品种识别接口。
    【权限】visitor：不可访问；user：可调用（受配额限制）；admin：可调用。
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """配额检查 → 加载图片 → 本地 CNN 推理 → 写调用日志。
        参数：request - 请求体含 image_url 或 image_base64、可选 description。
        返回：Response，含品种、置信度、候选列表等。
        【权限】需登录 user 或 admin。
        """
        # 先检查当前用户 AI 配额，若超限直接返回 429
        try:
            check_ai_quota(request.user)
        except AiQuotaExceededError as exc:
            return _ai_quota_response(exc, request.user, 'breed_detect')

        # 从请求中提取图片 URL、Base64 数据和可选描述
        image_url = (request.data.get('image_url') or '').strip()
        image_base64 = (request.data.get('image_base64') or '').strip()
        description = (request.data.get('description') or '').strip()
        # 将请求元信息写入日志，便于排查调用来源与参数情况
        meta = str({
            'image_url': image_url,
            'has_base64': bool(image_base64),
            'description': description,
        })
        # 分支：必须提供图片 URL 或 Base64 之一，否则直接返回 400
        if not image_url and not image_base64:
            return Response(
                {'detail': 'Please upload an image (image_url or image_base64).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # 调用本地品种识别入口，返回推理结果与候选信息
            payload = detect_pet_breed(
                image_url=image_url,
                image_base64=image_base64,
                description=description,
                request=request,
            )
            # 记录 AI 调用日志，成功时将结果写入日志表
            log = AiInvocationLog.objects.create(
                user=request.user, feature_type='breed_detect',
                request_meta=meta,
                result_meta=payload.get('debug_meta', payload['result']),
                success=True,
            )
            return Response({
                'result': payload['result'],
                'breed': payload['breed'],
                'species': payload.get('species', ''),
                'summary': payload.get('summary', ''),
                'breed_candidates': payload.get('breed_candidates', []),
                'low_confidence': payload.get('low_confidence', False),
                'confidence': payload['confidence'],
                'vision_used': payload.get('vision_used', False),
                'model_source': payload.get('model_source', 'local_cnn'),
                'object_recognition': payload.get('object_recognition', False),
                'object_labels': payload.get('object_labels', []),
                'log_id': log.id,
            })
        except ImageLoadError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except BreedModelNotReadyError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except (LLMNotConfiguredError, LLMRequestError) as exc:
            AiInvocationLog.objects.create(
                user=request.user, feature_type='breed_detect',
                request_meta=meta, result_meta=str(exc), success=False,
            )
            return _ai_error_response(exc)


class AiAdoptCopyView(APIView):
    """AI 领养文案：根据宠物字段调用 LLM 生成 Markdown 推介文案。
    【权限】visitor：不可访问；user：可调用（受配额限制）；admin：可调用。
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """配额检查 → 组装 Prompt → LLM 生成 → 写调用日志。
        参数：request - 请求体为宠物字段 JSON。
        返回：Response，含 copy 文案与 log_id。
        【权限】需登录 user 或 admin。
        """
        meta = str(request.data)
        try:
            check_ai_quota(request.user)
        except AiQuotaExceededError as exc:
            return _ai_quota_response(exc, request.user, 'adopt_copy', meta)

        pet_info = json.dumps(request.data, ensure_ascii=False)
        # 将原始请求数据转成 JSON 字符串，保留中文字段内容，作为 prompt 的输入内容
        pet_info = json.dumps(request.data, ensure_ascii=False)
        try:
            # 构造 LLM 调用的多轮消息，先给出角色指令，再附上用户问题
            copy_text = chat([
                {'role': 'system', 'content': '你是领养文案撰写助手，输出温暖中文领养介绍。请使用 Markdown 格式（标题、列表、加粗等）。'},
                {'role': 'user', 'content': f'根据以下宠物信息生成领养文案：{pet_info}'},
            ], max_tokens=800)
            # 记录 AI 调用日志，通常保存整个生成结果以便后续查询和审计
            log = AiInvocationLog.objects.create(
                user=request.user, feature_type='adopt_copy',
                request_meta=meta, result_meta=copy_text, success=True,
            )
            return Response({'copy': copy_text, 'log_id': log.id})
        except (LLMNotConfiguredError, LLMRequestError) as exc:
            AiInvocationLog.objects.create(
                user=request.user, feature_type='adopt_copy',
                request_meta=meta, result_meta=str(exc), success=False,
            )
            return _ai_error_response(exc)


class AiQaView(APIView):
    """AI 智能养宠问答：携带最近多轮上下文调用 LLM。
    【权限】visitor：不可访问；user：可调用（受配额限制）；admin：可调用。
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """配额检查 → 截取 history[-6] → LLM 回答 → 写调用日志。
        参数：request - 含 question 与可选 history 对话数组。
        返回：Response，含 answer 与 log_id。
        【权限】需登录 user 或 admin。
        """
        # 先从请求中读取 question 与历史对话列表
        question = request.data.get('question', '')
        history = request.data.get('history') or []
        try:
            check_ai_quota(request.user)
        except AiQuotaExceededError as exc:
            return _ai_quota_response(exc, request.user, 'qa_assistant', question)

        # 系统消息用于限定助手角色与输出风格
        messages = [{'role': 'system', 'content': '你是暖心救助平台的智能养宠助手，请用中文简明、专业地回答。'}]
        # 只保留最近 6 轮对话以降低 token 使用，并过滤掉无效项
        for item in history[-6:]:
            role = item.get('role')
            content = item.get('content')
            # 仅接受 user 和 assistant 角色数据，避免其它噪声输入
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
        # 将当前用户问题追加到对话末尾，作为本次 LLM 请求的触发语句
        messages.append({'role': 'user', 'content': question})
        try:
            answer = chat(messages, max_tokens=800)
            log = AiInvocationLog.objects.create(
                user=request.user, feature_type='qa_assistant',
                request_meta=question, result_meta=answer, success=True,
            )
            return Response({'answer': answer, 'log_id': log.id})
        except (LLMNotConfiguredError, LLMRequestError) as exc:
            AiInvocationLog.objects.create(
                user=request.user, feature_type='qa_assistant',
                request_meta=question, result_meta=str(exc), success=False,
            )
            return _ai_error_response(exc)


class AiLogPagination(PageNumberPagination):
    """AI 调用日志分页：默认每页 20 条。
    【权限】由 AdminAiLogViewSet 使用，仅 admin 可访问。
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminAiLogViewSet(viewsets.ReadOnlyModelViewSet):
    """AI 调用日志查询与用量统计。
    【权限】visitor：不可访问；user：不可访问；admin：可查询。
    """
    queryset = AiInvocationLog.objects.select_related('user').all()
    serializer_class = AiInvocationLogSerializer
    permission_classes = [IsAdminRole]
    pagination_class = AiLogPagination

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """管理员查询 AI 调用用量统计。
        参数：request - DRF 请求对象。
        返回：Response，含今日次数、累计次数、配额上限。
        【权限】仅 admin。
        """
        return Response(get_ai_usage_stats())
