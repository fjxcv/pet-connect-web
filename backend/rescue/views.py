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
        # 鎸夊綋鍓嶇敤鎴疯繃婊わ紙鎴戜笂鎶ョ殑锛�
        if self.request.query_params.get('my', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(reporter=self.request.user)
            else:
                return RescueCase.objects.none()
        # 鎸夋垜鏁戝姪鐨勮繃婊わ紙鎴戝搷搴旂殑锛�
        if self.request.query_params.get('helped', '').lower() == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(helpers=self.request.user)
            else:
                return RescueCase.objects.none()
        # 鎸夌姸鎬佽繃婊�
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
            qs = qs.filter(current_status__in=statuses)
        # 鎸夋晳鍔╃紪鍙风簿纭悳绱�
        rescue_no = self.request.query_params.get('rescue_no', '').strip()
        if rescue_no:
            qs = qs.filter(rescue_no__iexact=rescue_no)
        # 鎺掗櫎鎸囧畾鐘舵€�
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
            remark='琚彂鐜颁笂鎶�',
        )

    # POST /rescue/cases/{id}/help/ 鈥� 鐢ㄦ埛鍝嶅簲鏁戝姪
    @action(detail=True, methods=['post'], url_path='help')
    def help(self, request, pk=None):
        case = self.get_object()
        user = request.user
        if case.helpers.filter(id=user.id).exists():
            return Response({'detail': '鎮ㄥ凡鍝嶅簲杩囪鏁戝姪璁板綍'}, status=status.HTTP_400_BAD_REQUEST)
        case.helpers.add(user)
        # 棣栨鍝嶅簲鏃惰褰曟晳鍔╂棩鏈燂紝骞跺皢鐘舵€佷粠寰呮晳鍔╂帹杩涘埌鍖荤枟涓�
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
                remark=f'鐢ㄦ埛 {user.username} 鍝嶅簲鏁戝姪锛岀姸鎬佽嚜鍔ㄦ帹杩�',
            )
        write_operation_log(
            user, 'rescue', 'help',
            f'Rescue {case.rescue_no}: user {user.username} responded',
            'rescue_case', case.id, get_client_ip(request),
        )
        return Response(self.get_serializer(case).data)

    # 鐘舵€佹祦杞鍒欙細鍙兘鎺ㄨ繘鍒颁笅涓€涓姸鎬�
    STATUS_FLOW = {
        'in_medical': 'recovering',
        'recovering': 'awaiting_adoption',
        'awaiting_adoption': 'rescued',
    }

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        case = self.get_object()
        # 鏁戝姪浜烘垨绠＄悊鍛樻墠鑳芥洿鏂扮姸鎬�
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
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
        old_status = case.current_status
        expected_next = self.STATUS_FLOW.get(old_status)
        if expected_next is None:
            return Response(
                {'detail': f'褰撳墠鐘舵€�"{old_status}"涓嶅厑璁稿彉鏇�'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_status != expected_next:
            return Response(
                {'detail': f'鍙兘浠�"{old_status}"鍒囨崲鍒�"{expected_next}"'},
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

    # GET/POST /rescue/cases/{id}/stage-records/ 鈥� 鏌ョ湅/濉啓闃舵璁板綍
    @action(detail=True, methods=['get', 'post'], url_path='stage-records')
    def stage_records(self, request, pk=None):
        case = self.get_object()

        # GET锛氬垪鍑鸿妗堜緥鐨勬墍鏈夐樁娈佃褰�
        if request.method == 'GET':
            records = case.stage_records.select_related('operator').all()
            serializer = RescueStageRecordSerializer(records, many=True)
            return Response(serializer.data)

        # POST锛氭柊澧炰竴鏉￠樁娈佃褰�
        content = (request.data.get('content') or '').strip()
        if not content:
            return Response(
                {'detail': '璇峰～鍐欏綋鍓嶉樁娈电殑璇︾粏璁板綍'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 鏁戝姪浜烘垨绠＄悊鍛樻墠鑳藉～鍐�
        is_helper = case.helpers.filter(id=request.user.id).exists()
        is_admin = request.user.is_superuser or request.user.is_staff or (
            hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        )
        if not is_helper and not is_admin:
            return Response(
                {'detail': '鍙湁鏁戝姪浜烘垨绠＄悊鍛樻墠鑳藉～鍐欒褰�'},
                status=status.HTTP_403_FORBIDDEN,
            )

        record = RescueStageRecord.objects.create(
            rescue_case=case,
            content=content,
            operator=request.user,
        )
        serializer = RescueStageRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
