from datetime import datetime

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

<<<<<<< HEAD
from common.permissions import IsAdminRole
=======
from common.permissions import IsActiveUser, IsAdminRole
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
        # 按当前用户过滤（我上报的）
=======
        # 鎸夊綋鍓嶇敤鎴疯繃婊わ紙鎴戜笂鎶ョ殑锛�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        if self.request.query_params.get('my', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(reporter=self.request.user)
            else:
                return RescueCase.objects.none()
<<<<<<< HEAD
        # 按我救助的过滤（我响应的）
=======
        # 鎸夋垜鏁戝姪鐨勮繃婊わ紙鎴戝搷搴旂殑锛�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        if self.request.query_params.get('helped', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(helpers=self.request.user)
            else:
                return RescueCase.objects.none()
<<<<<<< HEAD
        # 按状态过滤
=======
        # 鎸夌姸鎬佽繃婊�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
            qs = qs.filter(current_status__in=statuses)
<<<<<<< HEAD
        # 按救助编号精确搜索
        rescue_no = self.request.query_params.get('rescue_no', '').strip()
        if rescue_no:
            qs = qs.filter(rescue_no__iexact=rescue_no)
        # 排除指定状态
=======
        # 鎸夋晳鍔╃紪鍙风簿纭悳绱�
        rescue_no = self.request.query_params.get('rescue_no', '').strip()
        if rescue_no:
            qs = qs.filter(rescue_no__iexact=rescue_no)
        # 鎺掗櫎鎸囧畾鐘舵€�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        exclude_status = self.request.query_params.get('exclude_status', '')
        if exclude_status:
            statuses = [s.strip() for s in exclude_status.split(',') if s.strip()]
            qs = qs.exclude(current_status__in=statuses)
        return qs.distinct()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action in ['create', 'help', 'update_status', 'stage_records']:
<<<<<<< HEAD
            return [permissions.IsAuthenticated()]
=======
            return [permissions.IsAuthenticated(), IsActiveUser()]
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        return [IsAdminRole()]

    def perform_create(self, serializer):
        case = serializer.save(reporter=self.request.user, rescue_no=generate_rescue_no())
        RescueStatusLog.objects.create(
            rescue_case=case,
            from_status=None,
            to_status=case.current_status,
            operator=self.request.user,
<<<<<<< HEAD
            remark='被发现上报',
        )

    # POST /rescue/cases/{id}/help/ — 用户响应救助
=======
            remark='琚彂鐜颁笂鎶�',
        )

    # POST /rescue/cases/{id}/help/ 鈥� 鐢ㄦ埛鍝嶅簲鏁戝姪
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    @action(detail=True, methods=['post'], url_path='help')
    def help(self, request, pk=None):
        case = self.get_object()
        user = request.user
        if case.helpers.filter(id=user.id).exists():
<<<<<<< HEAD
            return Response({'detail': '您已响应过该救助记录'}, status=status.HTTP_400_BAD_REQUEST)
        case.helpers.add(user)
        # 首次响应时记录救助日期，并将状态从待救助推进到医疗中
=======
            return Response({'detail': '鎮ㄥ凡鍝嶅簲杩囪鏁戝姪璁板綍'}, status=status.HTTP_400_BAD_REQUEST)
        case.helpers.add(user)
        # 棣栨鍝嶅簲鏃惰褰曟晳鍔╂棩鏈燂紝骞跺皢鐘舵€佷粠寰呮晳鍔╂帹杩涘埌鍖荤枟涓�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
                remark=f'用户 {user.username} 响应救助，状态自动推进',
=======
                remark=f'鐢ㄦ埛 {user.username} 鍝嶅簲鏁戝姪锛岀姸鎬佽嚜鍔ㄦ帹杩�',
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
            )
        write_operation_log(
            user, 'rescue', 'help',
            f'Rescue {case.rescue_no}: user {user.username} responded',
            'rescue_case', case.id, get_client_ip(request),
        )
        return Response(self.get_serializer(case).data)

<<<<<<< HEAD
    # 状态流转规则：只能推进到下一个状态
=======
    # 鐘舵€佹祦杞鍒欙細鍙兘鎺ㄨ繘鍒颁笅涓€涓姸鎬�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    STATUS_FLOW = {
        'in_medical': 'recovering',
        'recovering': 'awaiting_adoption',
        'awaiting_adoption': 'rescued',
    }

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        case = self.get_object()
<<<<<<< HEAD
        # 救助人或管理员才能更新状态
=======
        # 鏁戝姪浜烘垨绠＄悊鍛樻墠鑳芥洿鏂扮姸鎬�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
<<<<<<< HEAD
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
=======
            return Response({'detail': '鍙湁鏁戝姪浜烘垨绠＄悊鍛樻墠鑳芥洿鏂扮姸鎬�'}, status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('current_status')
        remark = (request.data.get('remark') or '').strip()

        # 鏍￠獙锛氱姸鎬佸€煎悎娉曟€�
        valid = dict(RescueCase.STATUS_CHOICES)
        if new_status not in valid:
            return Response({'detail': '鏃犳晥鐨勭姸鎬佸€�'}, status=status.HTTP_400_BAD_REQUEST)

        # 鏍￠獙锛氬娉ㄥ繀濉�
        if not remark:
            return Response({'detail': '璇峰～鍐欑姸鎬佸娉紙璇婃柇缁撴灉銆佹不鐤楁柟妗堢瓑锛�'}, status=status.HTTP_400_BAD_REQUEST)

        # 鏍￠獙锛氬彧鑳芥寜娴佽浆瑙勫垯鎺ㄨ繘
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        old_status = case.current_status
        expected_next = self.STATUS_FLOW.get(old_status)
        if expected_next is None:
            return Response(
<<<<<<< HEAD
                {'detail': f'当前状态"{old_status}"不允许变更'},
=======
                {'detail': f'褰撳墠鐘舵€�"{old_status}"涓嶅厑璁稿彉鏇�'},
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_status != expected_next:
            return Response(
<<<<<<< HEAD
                {'detail': f'只能从"{old_status}"切换到"{expected_next}"'},
=======
                {'detail': f'鍙兘浠�"{old_status}"鍒囨崲鍒�"{expected_next}"'},
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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

<<<<<<< HEAD
    # GET/POST /rescue/cases/{id}/stage-records/ — 查看/填写阶段记录
=======
    # GET/POST /rescue/cases/{id}/stage-records/ 鈥� 鏌ョ湅/濉啓闃舵璁板綍
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    @action(detail=True, methods=['get', 'post'], url_path='stage-records')
    def stage_records(self, request, pk=None):
        case = self.get_object()

<<<<<<< HEAD
        # GET：列出该案例的所有阶段记录
=======
        # GET锛氬垪鍑鸿妗堜緥鐨勬墍鏈夐樁娈佃褰�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        if request.method == 'GET':
            records = case.stage_records.select_related('operator').all()
            serializer = RescueStageRecordSerializer(records, many=True)
            return Response(serializer.data)

<<<<<<< HEAD
        # POST：新增一条阶段记录
        content = (request.data.get('content') or '').strip()
        if not content:
            return Response(
                {'detail': '请填写当前阶段的详细记录'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 救助人或管理员才能填写
=======
        # POST锛氭柊澧炰竴鏉￠樁娈佃褰�
        content = (request.data.get('content') or '').strip()
        if not content:
            return Response(
                {'detail': '璇峰～鍐欏綋鍓嶉樁娈电殑璇︾粏璁板綍'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 鏁戝姪浜烘垨绠＄悊鍛樻墠鑳藉～鍐�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
            return Response(
<<<<<<< HEAD
                {'detail': '只有救助人或管理员才能填写记录'},
=======
                {'detail': '鍙湁鏁戝姪浜烘垨绠＄悊鍛樻墠鑳藉～鍐欒褰�'},
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                status=status.HTTP_403_FORBIDDEN,
            )

        record = RescueStageRecord.objects.create(
            rescue_case=case,
            content=content,
            operator=request.user,
        )
        serializer = RescueStageRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
