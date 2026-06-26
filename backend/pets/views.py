"""
模块说明：pets 模块 API 视图。

提供宠物档案 CRUD、多维度筛选、附近搜索（Haversine）、
领养申请三步提交、管理员线上审核与线下核验等 HTTP 接口。
"""

import math

from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from common.permissions import IsAdminRole, user_is_admin
from common.utils import get_client_ip, write_operation_log
from .models import AdoptApplication, AdoptAttachment, AdoptOfflineVerify, AdoptQuestionnaire, PetProfile
from .serializers import (
    AdoptApplicationAuditSerializer,
    AdoptApplicationReviewDetailSerializer,
    AdoptApplicationSerializer,
    AdminAdoptApplicationListSerializer,
    AdoptAttachmentSerializer,
    AdoptOfflineVerifySerializer,
    AdoptQuestionnaireSerializer,
    PetProfileSerializer,
    PetProfileUpdateSerializer,
)


class PetProfileViewSet(viewsets.ModelViewSet):
    """
    宠物档案视图集。

    标准 REST：列表、详情、创建、更新、删除。
    扩展动作：nearby（附近搜索）、my_pets（我上报的宠物）。

    权限总览：
    - list / retrieve / nearby：visitor / user / admin 均可（仅 is_public=True 的档案）
    - my_pets：user / admin（需登录）
    - create / update / destroy：admin 专属
    """

    queryset = PetProfile.objects.all()
    serializer_class = PetProfileSerializer

    def get_serializer_class(self):
        """
        按动作选择序列化器：更新操作使用带额外校验的 PetProfileUpdateSerializer。

        返回:
            Serializer 类
        """
        if self.action in ['update', 'partial_update']:
            return PetProfileUpdateSerializer
        return PetProfileSerializer

    def get_permissions(self):
        """
        按动作动态分配接口权限。

        返回:
            list: 权限类实例列表
        """
        # 浏览列表、详情、附近搜索：游客也可访问
        if self.action in ['list', 'retrieve', 'nearby']:
            return [permissions.AllowAny()]
        # 查看我上报的宠物：须登录
        if self.action == 'my_pets':
            return [permissions.IsAuthenticated()]
        # 创建/编辑/删除宠物档案：仅 admin
        return [IsAdminRole()]

    def get_queryset(self):
        """
        构建宠物查询集，支持多维度筛选。

        查询参数:
            species: 物种（种类）
            gender: 性别
            size_category: 体型（small/medium/large）
            adoption_status: 领养状态
            search: 按名称模糊搜索
            location: 位置文字模糊匹配
            country / province / city: 地区筛选
            age_min / age_max: 年龄（月）区间
            is_public: 是否公开（admin 可指定）

        权限逻辑:
        - visitor / user 在 list/retrieve 时强制 is_public=True
        - admin 可查看全部档案

        返回:
            QuerySet: 过滤后的宠物查询集
        """
        qs = super().get_queryset().select_related('rescue_case')
        species = self.request.query_params.get('species')
        adoption_status = self.request.query_params.get('adoption_status')
        is_public = self.request.query_params.get('is_public')
        gender = self.request.query_params.get('gender')
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        country = self.request.query_params.get('country')
        province = self.request.query_params.get('province')
        city = self.request.query_params.get('city')
        age_min = self.request.query_params.get('age_min')
        age_max = self.request.query_params.get('age_max')
        size_category = self.request.query_params.get('size_category')
        if species:
            qs = qs.filter(species=species)
        if gender:
            qs = qs.filter(gender=gender)
        if size_category:
            qs = qs.filter(size_category=size_category)
        if adoption_status:
            qs = qs.filter(adoption_status=adoption_status)
        if search:
            qs = qs.filter(name__icontains=search)
        if location:
            qs = qs.filter(
                Q(location_text__icontains=location) |
                Q(rescue_case__discover_address__icontains=location)
            )
        if country:
            # 分支：中国地区兼容 country 为空的历史数据
            if country in ['中国', 'CN', 'cn']:
                qs = qs.filter(
                    Q(country__icontains=country) |
                    Q(country__isnull=True)
                )
            else:
                qs = qs.filter(country__icontains=country)
        if province:
            qs = qs.filter(
                Q(province__icontains=province) |
                Q(location_text__icontains=province) |
                Q(rescue_case__discover_address__icontains=province)
            )
        if city:
            qs = qs.filter(
                Q(city__icontains=city) |
                Q(location_text__icontains=city) |
                Q(rescue_case__discover_address__icontains=city)
            )
        if age_min:
            qs = qs.filter(age_months__gte=int(age_min))
        if age_max:
            qs = qs.filter(age_months__lte=int(age_max))
        # 【权限】非 admin 在列表/详情只能看 is_public=True
        if is_public is not None and self.action in ['list', 'retrieve']:
            if not (self.request.user.is_authenticated and getattr(self.request.user.profile, 'role', None) == 'admin'):
                qs = qs.filter(is_public=True)
        elif is_public is not None:
            qs = qs.filter(is_public=is_public.lower() == 'true')
        elif self.action in ['list', 'retrieve']:
            if not (self.request.user.is_authenticated and getattr(self.request.user.profile, 'role', None) == 'admin'):
                qs = qs.filter(is_public=True)
        return qs

    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """
        使用 Haversine 公式计算地球表面两点间球面距离（千米）。

        参数:
            lat1, lon1: 起点纬度、经度（用户当前位置）
            lat2, lon2: 终点纬度、经度（宠物或救助案例位置）
        返回:
            float: 距离（千米）
        """
        radius_km = 6371
        d_lat = math.radians(float(lat2) - float(lat1))
        d_lon = math.radians(float(lon2) - float(lon1))
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c

    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby(self, request):
        """
        附近宠物搜索接口。

        根据用户经纬度与半径（默认 5km），用 Haversine 公式计算距离并排序返回。
        宠物坐标优先用 latitude/longitude，缺失时回退 rescue_case 发现坐标。
        可选 same_province 限制同省/同城，减少远距离结果。

        权限：visitor / user / admin 均可（受 get_queryset 公开档案限制）。

        参数（query_params）:
            lat, lon: 用户当前经纬度（必填）
            radius_km / radius: 搜索半径千米，默认 5
            province, city: 可选地区预筛
            same_province: 是否限制同省/同城，默认 true

        返回:
            Response: 含 distance_km 字段的宠物列表，按距离升序
        """
        try:
            lat = float(request.query_params.get('lat', 0))
            lon = float(request.query_params.get('lon', 0))
            radius_km = float(request.query_params.get('radius_km') or request.query_params.get('radius') or 5)
        except (TypeError, ValueError):
            return Response({'detail': '请提供有效的经纬度参数（lat, lon）'}, status=status.HTTP_400_BAD_REQUEST)

        if not lat or not lon:
            return Response({'detail': '请提供经纬度参数'}, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset()

        province = (request.query_params.get('province') or '').strip()
        city = (request.query_params.get('city') or '').strip()
        same_province_raw = request.query_params.get('same_province')
        same_province = True if same_province_raw is None else same_province_raw.lower() in ('1', 'true', 'yes')
        # 分支：启用同省/同城预筛，缩小 Haversine 计算范围
        if same_province and (province or city):
            region_q = None
            if province:
                province_q = Q(province__icontains=province) | Q(rescue_case__discover_address__icontains=province)
                region_q = province_q if region_q is None else (region_q | province_q)
            if city:
                city_q = Q(city__icontains=city) | Q(rescue_case__discover_address__icontains=city)
                region_q = city_q if region_q is None else (region_q | city_q)
            if region_q is not None:
                qs = qs.filter(region_q)

        results = []
        for pet in qs:
            target_lat = pet.latitude or (pet.rescue_case.discover_latitude if pet.rescue_case else None)
            target_lon = pet.longitude or (pet.rescue_case.discover_longitude if pet.rescue_case else None)
            # 分支：无有效坐标则跳过该宠物
            if target_lat is None or target_lon is None:
                continue
            distance = self._haversine_distance(lat, lon, float(target_lat), float(target_lon))
            if distance <= radius_km:
                pet.distance_km = round(distance, 2)
                results.append(pet)

        results.sort(key=lambda item: item.distance_km)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my')
    def my_pets(self, request):
        """
        我上报的宠物列表。

        通过 rescue_case.reporter 关联，返回当前用户作为上报人救助后转入领养的宠物。

        权限：user / admin（需登录）。

        参数:
            request: 当前登录用户
        返回:
            Response: 宠物档案列表
        """
        qs = PetProfile.objects.filter(
            rescue_case__reporter=request.user,
        ).select_related('rescue_case')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AdoptApplicationViewSet(viewsets.ModelViewSet):
    """
    领养申请视图集。

    三步提交流程：
    1. POST create — 创建申请（宠物状态 → pending）
    2. POST .../questionnaire/ — 填写问卷 JSON
    3. POST .../attachments/ — 上传证明材料

    权限总览：
    - create / my / questionnaire / attachments / retrieve（本人）：user / admin
    - retrieve（任意申请）：admin
    - 其他写操作：admin
    """

    queryset = AdoptApplication.objects.select_related('applicant', 'pet', 'auditor', 'offline_verify').all()
    serializer_class = AdoptApplicationSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_permissions(self):
        """
        按动作分配权限：用户操作需登录，管理操作需 admin。

        返回:
            list: 权限类实例列表
        """
        if self.action in ['create', 'my', 'questionnaire', 'attachments']:
            return [permissions.IsAuthenticated()]
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def get_queryset(self):
        """
        按动作过滤申请范围。

        - my：仅当前用户的申请
        - retrieve：admin 看全部，user 仅看自己的
        - 其他：admin 管理用

        返回:
            QuerySet: 领养申请查询集
        """
        qs = self.queryset.prefetch_related('attachments').select_related('questionnaire')
        if self.action == 'my':
            return qs.filter(applicant=self.request.user)
        if self.action == 'retrieve':
            # 【权限】admin 可看任意申请；user 仅看自己的
            if user_is_admin(self.request.user):
                return qs
            return qs.filter(applicant=self.request.user)
        return qs

    def perform_create(self, serializer):
        """
        创建领养申请（三步流程第一步）。

        校验宠物可领养且无重复申请后，保存申请并将宠物状态改为 pending。

        权限：user / admin（需登录）。

        参数:
            serializer: 已通过校验的申请序列化器
        异常:
            ValidationError: 宠物不可领养或已有进行中申请
        """
        pet = serializer.validated_data['pet']
        # 分支：宠物当前不可领养
        if pet.adoption_status != 'available':
            raise ValidationError({'pet_id': '\u8be5\u5ba0\u7269\u5f53\u524d\u4e0d\u53ef\u7533\u8bf7\u9886\u517b'})
        # 分支：已有进行中的申请
        if AdoptApplication.objects.filter(
            pet=pet,
            online_status__in=['pending', 'approved'],
        ).exists():
            raise ValidationError({'pet_id': '\u8be5\u5ba0\u7269\u5df2\u6709\u8fdb\u884c\u4e2d\u7684\u9886\u517b\u7533\u8bf7'})
        app = serializer.save(applicant=self.request.user)
        app.pet.adoption_status = 'pending'
        app.pet.save(update_fields=['adoption_status', 'updated_at'])

    @action(detail=False, methods=['get'], url_path='my')
    def my(self, request):
        """
        我的领养申请列表。

        权限：user / admin（需登录）。

        参数:
            request: 当前登录用户
        返回:
            Response: 申请列表 JSON
        """
        qs = self.get_queryset()
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='questionnaire')
    def questionnaire(self, request, pk=None):
        """
        提交领养问卷（三步流程第二步）。

        将 answers_json 存入 AdoptQuestionnaire，每条申请仅可提交一次。

        权限：user 仅可对本人申请提交。

        参数:
            request: 请求体含 answers_json（问卷 JSON）
            pk: 申请 ID
        返回:
            Response: 201 成功或 400/403 错误
        """
        app = self.get_object()
        # 【权限】非本人禁止
        if app.applicant != request.user:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        # 分支：问卷已提交不可重复
        if hasattr(app, 'questionnaire'):
            return Response({'detail': 'Questionnaire already submitted'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdoptQuestionnaireSerializer(data={
            'application': app.id,
            'answers_json': request.data.get('answers_json', {}),
        })
        serializer.is_valid(raise_exception=True)
        AdoptQuestionnaire.objects.create(application=app, answers_json=serializer.validated_data['answers_json'])
        return Response({'detail': 'Questionnaire submitted'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='attachments')
    def attachments(self, request, pk=None):
        """
        上传领养申请附件（三步流程第三步）。

        保存证明材料元数据（file_type、file_url、file_size）。

        权限：user 仅可对本人申请上传。

        参数:
            request: 请求体含 file_type、file_url、file_size
            pk: 申请 ID
        返回:
            Response: 201 + 附件详情
        """
        app = self.get_object()
        # 【权限】非本人禁止
        if app.applicant != request.user:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AdoptAttachmentSerializer(data={
            'application': app.id,
            'file_type': request.data.get('file_type', 'other'),
            'file_url': request.data.get('file_url'),
            'file_size': request.data.get('file_size', 1),
        })
        serializer.is_valid(raise_exception=True)
        attachment = AdoptAttachment.objects.create(
            application=app,
            file_type=serializer.validated_data['file_type'],
            file_url=serializer.validated_data['file_url'],
            file_size=serializer.validated_data['file_size'],
        )
        return Response(AdoptAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class AdminAdoptApplicationViewSet(viewsets.GenericViewSet):
    """
    管理员领养审核视图集。

    提供申请列表、审核详情、线上审核（通过/拒绝/需补充材料）。

    权限：admin 专属。
    """

    queryset = AdoptApplication.objects.select_related(
        'applicant', 'applicant__profile', 'pet', 'pet__rescue_case', 'auditor',
    ).prefetch_related('attachments', 'questionnaire').all()
    serializer_class = AdoptApplicationAuditSerializer
    permission_classes = [IsAdminRole]

    def list(self, request):
        """
        领养申请列表（含问卷/附件完成度）。

        权限：admin。

        参数:
            request: HTTP 请求
        返回:
            Response: AdminAdoptApplicationListSerializer 列表
        """
        qs = self.get_queryset()
        serializer = AdminAdoptApplicationListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def review_detail(self, request, pk=None):
        """
        查看单条申请的审核详情（问卷 JSON、附件、脱敏手机号）。

        权限：admin。

        参数:
            request: HTTP 请求
            pk: 申请 ID
        返回:
            Response: AdoptApplicationReviewDetailSerializer 详情
        """
        app = self.get_object()
        return Response(AdoptApplicationReviewDetailSerializer(app).data)

    def update(self, request, pk=None):
        """
        线上审核领养申请（通过 / 拒绝 / 需补充材料）。

        审核后写入操作日志，并联动更新宠物领养状态。

        权限：admin。

        参数:
            request: 请求体含 online_status、audit_opinion
            pk: 申请 ID
        返回:
            Response: 更新后的申请数据
        """
        app = self.get_object()
        serializer = self.get_serializer(app, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        app.refresh_from_db()
        write_operation_log(
            request.user, 'adopt', 'audit',
            f'Adopt application audit #{app.id}: {app.online_status}',
            'adopt_application', app.id, get_client_ip(request),
        )
        return Response(AdoptApplicationSerializer(app).data)


class AdminOfflineVerifyViewSet(viewsets.GenericViewSet):
    """
    管理员线下核验视图集。

    线上审核通过后安排线下见面，录入核验结果并联动申请与宠物状态。

    权限：admin 专属。
    """

    queryset = AdoptOfflineVerify.objects.select_related('application').all()
    serializer_class = AdoptOfflineVerifySerializer
    permission_classes = [IsAdminRole]

    def update(self, request, pk=None):
        """
        更新线下核验结果（通过 / 失败）。

        规则：
        - failed 时必须填写 verify_note（失败原因）
        - passed → 申请 approved，宠物 adopted 并下架
        - failed → 申请 rejected，宠物恢复 available

        权限：admin。

        参数:
            request: 请求体含 verify_status、verify_note
            pk: 线下核验记录 ID
        返回:
            Response: 更新后的核验记录
        """
        verify = self.get_object()
        new_status = request.data.get('verify_status', verify.verify_status)
        verify_note = request.data.get('verify_note', verify.verify_note)
        # 分支：核验失败必须填写原因
        if new_status == 'failed' and not (verify_note or '').strip():
            return Response(
                {'verify_note': '\u6838\u9a8c\u5931\u8d25\u65f6\u5fc5\u987b\u586b\u5199\u5931\u8d25\u539f\u56e0'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        verify.verify_status = new_status
        verify.verify_note = verify_note
        verify.verifier = request.user
        verify.verified_at = timezone.now()
        verify.save()
        # 分支：线下核验通过
        if verify.verify_status == 'passed':
            verify.application.online_status = 'approved'
            verify.application.pet.adoption_status = 'adopted'
            verify.application.pet.is_public = False
        # 分支：线下核验失败，恢复可领养
        elif verify.verify_status == 'failed':
            verify.application.online_status = 'rejected'
            verify.application.pet.adoption_status = 'available'
        verify.application.save()
        verify.application.pet.save()
        return Response(AdoptOfflineVerifySerializer(verify).data)

    def create_for_application(self, request, application_id=None):
        """
        为指定申请单创建或获取线下核验记录。

        若已存在则直接返回，避免重复创建。

        权限：admin。

        参数:
            request: HTTP 请求
            application_id: 领养申请 ID
        返回:
            Response: 线下核验记录
        """
        app = AdoptApplication.objects.get(pk=application_id)
        verify, _ = AdoptOfflineVerify.objects.get_or_create(application=app)
        return Response(AdoptOfflineVerifySerializer(verify).data)
