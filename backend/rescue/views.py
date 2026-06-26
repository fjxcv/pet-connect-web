# -*- coding: utf-8 -*-
"""
模块说明：rescue 模块 API 视图。

提供救助案例上报、列表筛选、响应救助（help）、
状态机推进、阶段记录与时间线等 HTTP 接口。
"""

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
    """
    救助案例列表分页配置。

    默认每页 10 条，客户端可通过 page_size 调整（最大 50）。
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class RescueCaseViewSet(viewsets.ModelViewSet):
    """
    救助案例视图集。

    标准 REST + 扩展动作：help（响应救助）、update_status（状态推进）、stage_records（阶段记录）。

    权限总览：
    - list / retrieve：visitor / user / admin 均可
    - create / help / update_status / stage_records：user / admin（须登录且未封禁）
    - update / destroy：admin 专属

    状态机流转（单向推进）：
    pending_rescue → in_medical → recovering → awaiting_adoption → rescued
    （help 动作可将 pending_rescue 自动推进到 in_medical）
    """

    queryset = RescueCase.objects.select_related('reporter').prefetch_related('status_logs').all()
    serializer_class = RescueCaseSerializer
    pagination_class = RescueCasePagination

    def get_queryset(self):
        """
        构建救助案例查询集，支持多种筛选。

        查询参数:
            my=true: 我上报的救助（须登录）
            helped=true: 我响应的救助（须登录）
            status: 按当前状态筛选，逗号分隔多值
            rescue_no: 按救助编号精确搜索
            exclude_status: 排除指定状态，逗号分隔

        权限逻辑:
        - my / helped 未登录时返回空结果

        返回:
            QuerySet: 去重后的救助案例查询集
        """
        qs = RescueCase.objects.select_related('reporter').prefetch_related('status_logs', 'helpers')
        # 分支：按当前用户过滤「我上报的」
        if self.request.query_params.get('my', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(reporter=self.request.user)
            else:
                return RescueCase.objects.none()
        # 分支：按当前用户过滤「我响应的」
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
        """
        按动作动态分配接口权限。

        返回:
            list: 权限类实例列表
        """
        # 浏览列表与详情：游客也可访问
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        # 上报、响应、更新状态、阶段记录：登录且账号正常
        if self.action in ['create', 'help', 'update_status', 'stage_records']:
            return [permissions.IsAuthenticated(), IsActiveUser()]
        # 编辑/删除案例：仅 admin
        return [IsAdminRole()]

    def perform_create(self, serializer):
        """
        创建救助案例（用户上报）。

        自动生成 rescue_no（RES+日期+流水号），写入首条状态日志。
        上报数据含 GPS 坐标与 discover_address（前端高德逆地理编码填充）。

        权限：user / admin（须登录）。

        参数:
            serializer: 已通过校验的案例序列化器
        """
        case = serializer.save(reporter=self.request.user, rescue_no=generate_rescue_no())
        RescueStatusLog.objects.create(
            rescue_case=case,
            from_status=None,
            to_status=case.current_status,
            operator=self.request.user,
            remark='\u88ab\u53d1\u73b0\u4e0a\u62a5',
        )

    # POST /rescue/cases/{id}/help/ — 用户响应救助
    @action(detail=True, methods=['post'], url_path='help')
    def help(self, request, pk=None):
        """
        响应救助接口（POST /rescue/cases/{id}/help/）。

        用户点击「我要帮助」后加入 helpers 列表；
        首次响应时记录 help_date，并将 pending_rescue 自动推进到 in_medical。
        前端可弹窗展示上报人 contact 联系方式。

        权限：user / admin（须登录且未封禁）。

        参数:
            request: 当前登录用户
            pk: 救助案例 ID
        返回:
            Response: 更新后的案例详情（含 helpers、status_logs）
        """
        case = self.get_object()
        user = request.user
        # 分支：已响应过不可重复
        if case.helpers.filter(id=user.id).exists():
            return Response({'detail': '\u60a8\u5df2\u54cd\u5e94\u8be5\u6551\u52a9\u8bb0\u5f55'}, status=status.HTTP_400_BAD_REQUEST)
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
        # 分支：状态发生变化时写入时间线日志
        if old_status != case.current_status:
            RescueStatusLog.objects.create(
                rescue_case=case,
                from_status=old_status,
                to_status=case.current_status,
                operator=user,
                remark=f'\u7528\u6237 {user.username} \u54cd\u5e94\u6551\u52a9\uff0c\u72b6\u6001\u81ea\u52a8\u63a8\u8fdb',
            )
        write_operation_log(
            user, 'rescue', 'help',
            f'Rescue {case.rescue_no}: user {user.username} responded',
            'rescue_case', case.id, get_client_ip(request),
        )
        return Response(self.get_serializer(case).data)

    # 状态流转规则：只能按顺序推进到下一个状态
    STATUS_FLOW = {
        'in_medical': 'recovering',
        'recovering': 'awaiting_adoption',
        'awaiting_adoption': 'rescued',
    }

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        手动推进救助状态接口（PATCH /rescue/cases/{id}/status/）。

        严格按 STATUS_FLOW 单向推进，每次变更 remark 备注必填。
        合法路径：in_medical→recovering→awaiting_adoption→rescued。

        权限：救助响应者（helpers）或 admin；其他人 403。

        参数:
            request: 请求体含 current_status（目标状态）、remark（必填备注）
            pk: 救助案例 ID
        返回:
            Response: 更新后的案例详情或 400/403 错误
        """
        case = self.get_object()
        # 【权限】救助人或管理员才能更新状态
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
            return Response({'detail': '\u53ea\u6709\u6551\u52a9\u4eba\u6216\u7ba1\u7406\u5458\u624d\u80fd\u66f4\u65b0\u72b6\u6001'}, status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('current_status')
        remark = (request.data.get('remark') or '').strip()
        # 校验：状态值合法性
        valid = dict(RescueCase.STATUS_CHOICES)
        if new_status not in valid:
            return Response({'detail': '\u65e0\u6548\u7684\u72b6\u6001\u503c'}, status=status.HTTP_400_BAD_REQUEST)
        # 校验：备注必填（诊断结果、治疗方案等）
        if not remark:
            return Response({'detail': '\u8bf7\u586b\u5199\u72b6\u6001\u5907\u6ce8\uff08\u8bca\u65ad\u7ed3\u679c\u3001\u6cbb\u7597\u65b9\u6848\u7b49\uff09'}, status=status.HTTP_400_BAD_REQUEST)
        # 校验：只能按流转规则推进
        old_status = case.current_status
        expected_next = self.STATUS_FLOW.get(old_status)
        if expected_next is None:
            return Response(
                {'detail': f'\u5f53\u524d\u72b6\u6001\u201c{old_status}\u201d\u4e0d\u5141\u8bb8\u53d8\u66f4'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_status != expected_next:
            return Response(
                {'detail': f'\u53ea\u80fd\u4ece\u201c{old_status}\u201d\u5207\u6362\u5230\u201c{expected_next}\u201d'},
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
        """
        救助阶段记录接口（GET/POST /rescue/cases/{id}/stage-records/）。

        GET：列出该案例全部阶段记录（时间倒序）。
        POST：新增一条阶段记录，content 正文必填。

        权限：
        - GET：visitor / user / admin 均可
        - POST：救助响应者（helpers）或 admin

        参数:
            request: GET 无体；POST 含 content
            pk: 救助案例 ID
        返回:
            Response: GET 为记录列表；POST 为 201 + 新记录
        """
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
                {'detail': '\u8bf7\u586b\u5199\u5f53\u524d\u9636\u6bb5\u7684\u8be6\u7ec6\u8bb0\u5f55'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 【权限】救助人或管理员才能填写
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
            return Response(
                {'detail': '\u53ea\u6709\u6551\u52a9\u4eba\u6216\u7ba1\u7406\u5458\u624d\u80fd\u586b\u5199\u8bb0\u5f55'},
                status=status.HTTP_403_FORBIDDEN,
            )
        record = RescueStageRecord.objects.create(
            rescue_case=case,
            content=content,
            operator=request.user,
        )
        serializer = RescueStageRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
