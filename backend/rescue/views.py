from datetime import datetime

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from common.permissions import IsActiveUser, IsAdminRole
from common.utils import get_client_ip, write_operation_log
from .models import RescueCase, RescueStageRecord, RescueStatusLog
from .serializers import RescueCaseSerializer, RescueStageRecordSerializer, generate_rescue_no


class RescueCasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class RescueCaseViewSet(viewsets.ModelViewSet):
    queryset = RescueCase.objects.select_related('reporter').prefetch_related('status_logs').all()
    serializer_class = RescueCaseSerializer
    pagination_class = RescueCasePagination

    def get_queryset(self):
        qs = RescueCase.objects.select_related('reporter').prefetch_related('status_logs', 'helpers')
        # 按当前用户过滤（我上报的）
        if self.request.query_params.get('my', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(reporter=self.request.user)
            else:
                return RescueCase.objects.none()
        # 按我救助的过滤（我响应的）
        if self.request.query_params.get('helped', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(helpers=self.request.user)
            else:
                return RescueCase.objects.none()
        # 按状态过滤
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
            qs = qs.filter(current_status__in=statuses)
        # 按救助编号精确搜索
        rescue_no = self.request.query_params.get('rescue_no', '').strip()
        if rescue_no:
            qs = qs.filter(rescue_no__iexact=rescue_no)
        # 排除指定状态
        exclude_status = self.request.query_params.get('exclude_status', '')
        if exclude_status:
            statuses = [s.strip() for s in exclude_status.split(',') if s.strip()]
            qs = qs.exclude(current_status__in=statuses)
        return qs.distinct()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action in ['create', 'help', 'update_status', 'stage_records']:
            return [permissions.IsAuthenticated(), IsActiveUser()]
        return [IsAdminRole()]

    def perform_create(self, serializer):
        case = serializer.save(reporter=self.request.user, rescue_no=generate_rescue_no())
        RescueStatusLog.objects.create(
            rescue_case=case,
            from_status=None,
            to_status=case.current_status,
            operator=self.request.user,
            remark='被发现上报',
        )

    # POST /rescue/cases/{id}/help/ — 用户响应救助
    @action(detail=True, methods=['post'], url_path='help')
    def help(self, request, pk=None):
        case = self.get_object()
        user = request.user
        if case.helpers.filter(id=user.id).exists():
            return Response({'detail': '您已响应该救助记录'}, status=status.HTTP_400_BAD_REQUEST)
        case.helpers.add(user)
        # 首次响应时记录救助日期，并将状态从待救助推进到医疗中
        if case.help_date is None:
            case.help_date = datetime.now()
        old_status = case.current_status
        if old_status == 'pending_rescue':
            case.current_status = 'in_medical'
        update_fields = ['current_status', 'updated_at']
        if case.help_date:
            update_fields.append('help_date')
        case.save(update_fields=update_fields)
        if old_status != case.current_status:
            RescueStatusLog.objects.create(
                rescue_case=case,
                from_status=old_status,
                to_status=case.current_status,
                operator=user,
                remark=f'用户 {user.username} 响应救助，状态自动推进',
            )
        write_operation_log(
            user, 'rescue', 'help',
            f'Rescue {case.rescue_no}: user {user.username} responded',
            'rescue_case', case.id, get_client_ip(request),
        )
        return Response(self.get_serializer(case).data)

    # 状态流转规则：只能推进到下一个状态
    STATUS_FLOW = {
        'in_medical': 'recovering',
        'recovering': 'awaiting_adoption',
        'awaiting_adoption': 'rescued',
    }

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        case = self.get_object()
        # 救助人或管理员才能更新状态
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
            return Response({'detail': '只有救助人或管理员才能更新状态'}, status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('current_status')
        remark = (request.data.get('remark') or '').strip()

        # 校验：状态值合法性
        valid = dict(RescueCase.STATUS_CHOICES)
        if new_status not in valid:
            return Response({'detail': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)

        # 校验：备注必填
        if not remark:
            return Response({'detail': '请填写状态备注（诊断结果、治疗方案等）'}, status=status.HTTP_400_BAD_REQUEST)

        # 校验：只能按流转规则推进
        old_status = case.current_status
        expected_next = self.STATUS_FLOW.get(old_status)
        if expected_next is None:
            return Response(
                {'detail': f'当前状态"{old_status}"不允许变更'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_status != expected_next:
            return Response(
                {'detail': f'只能从"{old_status}"切换到"{expected_next}"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.current_status = new_status
        case.save(update_fields=['current_status', 'updated_at'])
        RescueStatusLog.objects.create(
            rescue_case=case,
            from_status=old_status,
            to_status=new_status,
            operator=request.user,
            remark=remark,
        )
        write_operation_log(
            request.user, 'rescue', 'status_change',
            f'Rescue {case.rescue_no}: {old_status} -> {new_status}',
            'rescue_case', case.id, get_client_ip(request),
        )
        return Response(self.get_serializer(case).data)

    # GET/POST /rescue/cases/{id}/stage-records/ — 查看/填写阶段记录
    @action(detail=True, methods=['get', 'post'], url_path='stage-records')
    def stage_records(self, request, pk=None):
        case = self.get_object()

        # GET：列出该案例的所有阶段记录
        if request.method == 'GET':
            records = case.stage_records.select_related('operator').all()
            serializer = RescueStageRecordSerializer(records, many=True)
            return Response(serializer.data)

        # POST：新增一条阶段记录
        content = (request.data.get('content') or '').strip()
        if not content:
            return Response(
                {'detail': '请填写当前阶段的详细记录'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 救助人或管理员才能填写
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
            return Response(
                {'detail': '只有救助人或管理员才能填写记录'},
                status=status.HTTP_403_FORBIDDEN,
            )

        record = RescueStageRecord.objects.create(
            rescue_case=case,
            content=content,
            operator=request.user,
        )
        serializer = RescueStageRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
