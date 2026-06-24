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
    permission_classes = [IsAdminRole]

    def get(self, request):
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
    queryset = User.objects.select_related('profile').all()
    permission_classes = [IsAdminRole]

    def list(self, request):
        users = self.get_queryset()
        role = request.query_params.get('role')
        status_val = request.query_params.get('status')
        if role:
            users = users.filter(profile__role=role)
        if status_val is not None:
            users = users.filter(profile__status=int(status_val))
        return Response(UserSerializer(users[:100], many=True).data)

    def partial_update(self, request, pk=None):
        user = User.objects.get(pk=pk)
        profile = user.profile
        if 'status' in request.data:
            profile.status = int(request.data['status'])
        if 'role' in request.data:
            profile.role = request.data['role']
        profile.save()
        write_operation_log(
            request.user, 'admin', 'user_update',
            f'Updated user {user.username}',
            'user', user.id, get_client_ip(request),
        )
        return Response(UserSerializer(user).data)


class AdminModerationViewSet(viewsets.ModelViewSet):
    queryset = ContentModeration.objects.select_related('operator').all()
    serializer_class = ContentModerationSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        mod = serializer.save(operator=self.request.user)
        try:
            apply_moderation(mod.content_type, mod.content_id, mod.action)
        except ValueError as exc:
            mod.delete()
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': str(exc)}) from exc
        write_operation_log(
            self.request.user, 'moderation', mod.action,
            f'{mod.content_type}#{mod.content_id}: {mod.action}',
            mod.content_type, mod.content_id, get_client_ip(self.request),
        )


class AdminConfigViewSet(viewsets.ModelViewSet):
    queryset = PlatformConfig.objects.all()
    serializer_class = PlatformConfigSerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'config_key'


class AdminOperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationLog.objects.select_related('operator').all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAdminRole]


def _ai_error_response(exc):
    if isinstance(exc, LLMNotConfiguredError):
        return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


def _ai_quota_response(exc, user, feature_type, request_meta=''):
    log_quota_exceeded(user, feature_type, request_meta)
    return Response({'detail': str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)


class AiBreedDetectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            check_ai_quota(request.user)
        except AiQuotaExceededError as exc:
            return _ai_quota_response(exc, request.user, 'breed_detect')

        image_url = (request.data.get('image_url') or '').strip()
        image_base64 = (request.data.get('image_base64') or '').strip()
        description = (request.data.get('description') or '').strip()
        meta = str({
            'image_url': image_url,
            'has_base64': bool(image_base64),
            'description': description,
        })
        if not image_url and not image_base64:
            return Response(
                {'detail': 'Please upload an image (image_url or image_base64).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payload = detect_pet_breed(
                image_url=image_url,
                image_base64=image_base64,
                description=description,
                request=request,
            )
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        meta = str(request.data)
        try:
            check_ai_quota(request.user)
        except AiQuotaExceededError as exc:
            return _ai_quota_response(exc, request.user, 'adopt_copy', meta)

        pet_info = json.dumps(request.data, ensure_ascii=False)
        try:
            copy_text = chat([
<<<<<<< HEAD
                {'role': 'system', 'content': '\u4f60\u662f\u9886\u517b\u6587\u6848\u64b0\u5199\u52a9\u624b\uff0c\u8f93\u51fa\u6e29\u6696\u4e2d\u6587\u9886\u517b\u4ecb\u7ecd\u3002'},
=======
                {'role': 'system', 'content': '\u4f60\u662f\u9886\u517b\u6587\u6848\u64b0\u5199\u52a9\u624b\uff0c\u8f93\u51fa\u6e29\u6696\u4e2d\u6587\u9886\u517b\u4ecb\u7ecd\u3002\u8bf7\u4f7f\u7528 Markdown \u683c\u5f0f\uff08\u6807\u9898\u3001\u5217\u8868\u3001\u52a0\u7c97\u7b49\uff09\u3002'},
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                {'role': 'user', 'content': f'\u6839\u636e\u4ee5\u4e0b\u5ba0\u7269\u4fe1\u606f\u751f\u6210\u9886\u517b\u6587\u6848\uff1a{pet_info}'},
            ], max_tokens=800)
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question = request.data.get('question', '')
        history = request.data.get('history') or []
        try:
            check_ai_quota(request.user)
        except AiQuotaExceededError as exc:
            return _ai_quota_response(exc, request.user, 'qa_assistant', question)

        messages = [{'role': 'system', 'content': '\u4f60\u662f\u6696\u722a\u6551\u52a9\u5e73\u53f0\u7684\u667a\u80fd\u517b\u5ba0\u52a9\u624b\uff0c\u8bf7\u7528\u4e2d\u6587\u7b80\u6d01\u3001\u4e13\u4e1a\u5730\u56de\u7b54\u3002'}]
        for item in history[-6:]:
            role = item.get('role')
            content = item.get('content')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
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
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminAiLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AiInvocationLog.objects.select_related('user').all()
    serializer_class = AiInvocationLogSerializer
    permission_classes = [IsAdminRole]
    pagination_class = AiLogPagination

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response(get_ai_usage_stats())
