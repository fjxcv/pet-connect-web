"""
模块说明：pets 模块序列化器。

负责宠物档案、领养申请三步流程（申请→问卷→附件）、
管理员线上审核与线下核验等数据的校验与 JSON 转换。
"""

from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import UserSerializer
from pets.models import AdoptApplication, AdoptAttachment, AdoptOfflineVerify, AdoptQuestionnaire, PetProfile


class PetProfileSerializer(serializers.ModelSerializer):
    """
    宠物档案序列化器。

    用于宠物列表/详情/附近搜索的响应体；
    附加衍生字段便于前端展示，distance_km 由 nearby 视图注入。

    权限：
    - visitor / user：只读公开字段
    - admin：可创建/编辑/删除宠物档案
    """

    # 展示用地址：优先 location_text，否则回退救助案例发现地址
    rescue_case_address = serializers.SerializerMethodField()
    # 关联救助案例的外观描述
    rescue_case_appearance = serializers.SerializerMethodField()
    # 体型中文展示文本
    size_category_display = serializers.SerializerMethodField()
    # 救助案例纬度（附近搜索坐标回退来源）
    rescue_case_latitude = serializers.SerializerMethodField()
    # 救助案例经度
    rescue_case_longitude = serializers.SerializerMethodField()
    # 与当前定位的距离（千米），由视图层 Haversine 计算后赋值
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = PetProfile
        fields = '__all__'

    def get_rescue_case_address(self, obj):
        """
        获取展示用地址文本。

        参数:
            obj (PetProfile): 宠物实例
        返回:
            str | None: 位置描述或救助发现地址
        """
        if obj.location_text:
            return obj.location_text
        if obj.rescue_case:
            return obj.rescue_case.discover_address
        return None

    def get_rescue_case_appearance(self, obj):
        """
        获取关联救助案例的外观描述。

        参数:
            obj (PetProfile): 宠物实例
        返回:
            str | None: 毛色、特征等描述
        """
        if obj.rescue_case:
            return obj.rescue_case.appearance
        return None

    def get_size_category_display(self, obj):
        """
        获取体型的友好展示文本（如「小型」「中型」「大型」）。

        参数:
            obj (PetProfile): 宠物实例
        返回:
            str | None: 展示文本，未设置体型时返回 None
        """
        return obj.get_size_category_display() if obj.size_category else None

    def get_rescue_case_latitude(self, obj):
        """
        获取救助案例发现纬度（宠物自身无坐标时的回退来源）。

        参数:
            obj (PetProfile): 宠物实例
        返回:
            Decimal | None: 纬度
        """
        if obj.rescue_case:
            return obj.rescue_case.discover_latitude
        return None

    def get_rescue_case_longitude(self, obj):
        """
        获取救助案例发现经度。

        参数:
            obj (PetProfile): 宠物实例
        返回:
            Decimal | None: 经度
        """
        if obj.rescue_case:
            return obj.rescue_case.discover_longitude
        return None

    def validate(self, attrs):
        """
        校验地址相关必填字段。

        规则：创建时或显式修改地址字段时，country/province/city/location_text 均不能为空。
        通常在 admin 创建/编辑宠物档案时触发。

        参数:
            attrs (dict): 待写入字段
        返回:
            dict: 校验并 strip 后的 attrs
        异常:
            ValidationError: 缺少必填地址字段时
        """
        required_fields = ['country', 'province', 'city', 'location_text']
        is_create = self.instance is None
        touched_location = any(field in attrs for field in required_fields)
        if is_create or touched_location:
            missing = []
            for field in required_fields:
                value = attrs.get(field, getattr(self.instance, field, None))
                if isinstance(value, str):
                    value = value.strip()
                    if field in attrs:
                        attrs[field] = value
                if not value:
                    missing.append(field)
            if missing:
                raise serializers.ValidationError({
                    field: '该字段为必填项' for field in missing
                })
        return attrs


class AdoptApplicationSerializer(serializers.ModelSerializer):
    """
    领养申请序列化器。

    用户提交领养申请（三步流程第一步）时使用；
    包含只读的申请人、宠物信息，以及 write_only 的 pet_id。

    权限：user（需登录）可创建；admin 可查看全部。
    """

    applicant = UserSerializer(read_only=True)
    pet = PetProfileSerializer(read_only=True)
    # 写入时传 pet_id，映射到 pet 外键
    pet_id = serializers.PrimaryKeyRelatedField(
        queryset=PetProfile.objects.all(), source='pet', write_only=True
    )
    # 线下核验状态（来自 AdoptOfflineVerify，只读）
    verify_status = serializers.SerializerMethodField()
    verify_note = serializers.SerializerMethodField()

    class Meta:
        model = AdoptApplication
        fields = [
            'id', 'applicant', 'pet', 'pet_id', 'online_status', 'audit_opinion',
            'auditor', 'audited_at', 'message', 'created_at', 'updated_at',
            'verify_status', 'verify_note',
        ]
        read_only_fields = ['applicant', 'auditor', 'audited_at', 'created_at', 'updated_at',
                            'verify_status', 'verify_note']

    def get_verify_status(self, obj):
        """
        获取关联的线下核验状态。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            str | None: scheduled/passed/failed，无记录时 None
        """
        try:
            return obj.offline_verify.verify_status
        except AdoptOfflineVerify.DoesNotExist:
            return None

    def get_verify_note(self, obj):
        """
        获取线下核验备注。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            str | None: 核验备注
        """
        try:
            return obj.offline_verify.verify_note
        except AdoptOfflineVerify.DoesNotExist:
            return None

    def validate(self, attrs):
        """
        创建申请前的业务校验。

        规则：
        - 目标宠物 adoption_status 必须为 available（可领养）
        - 同一宠物不得存在 pending 或 approved 的进行中申请
        - 同一用户不得对同一宠物重复提交 pending/approved 申请

        参数:
            attrs (dict): 含 pet 的待校验数据
        返回:
            dict: 校验通过的 attrs
        异常:
            ValidationError: 不满足业务规则时
        """
        pet = attrs.get('pet') or getattr(self.instance, 'pet', None)
        applicant = self.context['request'].user
        if pet and pet.adoption_status != 'available':
            raise serializers.ValidationError('\u8be5\u5ba0\u7269\u5f53\u524d\u4e0d\u53ef\u7533\u8bf7\u9886\u517b')
        if pet and AdoptApplication.objects.filter(
            pet=pet,
            online_status__in=['pending', 'approved'],
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('\u8be5\u5ba0\u7269\u5df2\u6709\u8fdb\u884c\u4e2d\u7684\u9886\u517b\u7533\u8bf7')
        if pet and AdoptApplication.objects.filter(
            applicant=applicant,
            pet=pet,
            online_status__in=['pending', 'approved'],
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('\u60a8\u5df2\u63d0\u4ea4\u8fc7\u8be5\u5ba0\u7269\u7684\u9886\u517b\u7533\u8bf7')
        return attrs


class AdoptQuestionnaireSerializer(serializers.ModelSerializer):
    """
    领养问卷序列化器（三步流程第二步）。

    answers_json 存储前端提交的问卷 JSON，submitted_at 由服务端自动记录。

    权限：user 仅可对本人申请提交一次问卷。
    """

    class Meta:
        model = AdoptQuestionnaire
        fields = ['id', 'application', 'answers_json', 'submitted_at']
        read_only_fields = ['application', 'submitted_at']


class AdoptAttachmentSerializer(serializers.ModelSerializer):
    """
    领养附件序列化器（三步流程第三步）。

    接收文件元数据（类型、URL、大小），实际文件由前端上传至存储后传入 URL。

    权限：user 仅可对本人申请上传附件。
    """

    class Meta:
        model = AdoptAttachment
        fields = ['id', 'application', 'file_type', 'file_url', 'file_size', 'uploaded_at']
        read_only_fields = ['application', 'uploaded_at']

    def validate_file_size(self, value):
        """
        校验上传文件大小为正值。

        参数:
            value (int): 文件字节数
        返回:
            int: 校验通过的大小
        异常:
            ValidationError: 大小 <= 0 时
        """
        if value <= 0:
            raise serializers.ValidationError('File size must be greater than 0')
        return value


class AdoptOfflineVerifySerializer(serializers.ModelSerializer):
    """
    线下核验序列化器。

    管理员记录线下见面核验结果（通过/失败）及备注。

    权限：admin 可创建/更新。
    """

    class Meta:
        model = AdoptOfflineVerify
        fields = ['id', 'application', 'verify_status', 'verify_note', 'verifier', 'verified_at']
        read_only_fields = ['application', 'verifier', 'verified_at']


class AdminAdoptApplicationListSerializer(serializers.ModelSerializer):
    """
    管理员领养申请列表序列化器。

    用于后台列表页，附加 has_questionnaire、attachment_count 便于快速了解材料完整度。

    权限：admin 只读。
    """

    applicant = UserSerializer(read_only=True)
    pet = PetProfileSerializer(read_only=True)
    # 是否已填写问卷（第二步）
    has_questionnaire = serializers.SerializerMethodField()
    # 已上传附件数量（第三步）
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = AdoptApplication
        fields = [
            'id', 'applicant', 'pet', 'online_status', 'audit_opinion', 'message',
            'created_at', 'has_questionnaire', 'attachment_count',
        ]

    def get_has_questionnaire(self, obj):
        """
        判断申请是否已提交问卷。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            bool: 已提交为 True
        """
        try:
            obj.questionnaire
            return True
        except AdoptQuestionnaire.DoesNotExist:
            return False

    def get_attachment_count(self, obj):
        """
        统计申请已上传的附件数量。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            int: 附件条数
        """
        return obj.attachments.count()


class AdoptApplicationAuditSerializer(serializers.ModelSerializer):
    """
    领养线上审核序列化器。

    管理员审核接口使用，可设置 online_status（通过/拒绝/需补充材料）与 audit_opinion。
    审核通过时自动将宠物标记为已领养并隐藏；拒绝时若无其他进行中申请则恢复可领养。

    权限：admin 可写。
    """

    class Meta:
        model = AdoptApplication
        fields = ['online_status', 'audit_opinion']

    def validate(self, attrs):
        """
        审核校验：拒绝时必须填写驳回原因。

        参数:
            attrs (dict): 含 online_status、audit_opinion
        返回:
            dict: 校验通过的 attrs
        异常:
            ValidationError: 拒绝但 audit_opinion 为空时
        """
        online_status = attrs.get('online_status')
        audit_opinion = attrs.get('audit_opinion', '')
        if online_status == 'rejected' and not audit_opinion.strip():
            raise serializers.ValidationError({'audit_opinion': '\u62d2\u7edd\u65f6\u5fc5\u987b\u586b\u5199\u9a73\u56de\u539f\u56e0'})
        return attrs

    def update(self, instance, validated_data):
        """
        执行审核并联动更新宠物领养状态。

        参数:
            instance (AdoptApplication): 待审核申请
            validated_data (dict): 审核结果字段
        返回:
            AdoptApplication: 更新后的申请实例
        """
        instance.online_status = validated_data.get('online_status', instance.online_status)
        instance.audit_opinion = validated_data.get('audit_opinion', instance.audit_opinion)
        instance.auditor = self.context['request'].user
        instance.audited_at = timezone.now()
        instance.save()
        # 分支：审核通过 → 宠物标记已领养并下架
        if instance.online_status == 'approved':
            instance.pet.adoption_status = 'adopted'
            instance.pet.is_public = False
            instance.pet.save(update_fields=['adoption_status', 'is_public', 'updated_at'])
        # 分支：审核拒绝 → 若无其他进行中/已通过申请，恢复宠物为可领养
        elif instance.online_status == 'rejected':
            if not AdoptApplication.objects.filter(pet=instance.pet, online_status__in=['pending', 'approved']).exclude(pk=instance.pk).exists():
                instance.pet.adoption_status = 'available'
                instance.pet.save(update_fields=['adoption_status', 'updated_at'])
        return instance


class AdoptApplicationReviewDetailSerializer(serializers.ModelSerializer):
    """
    领养审核详情序列化器。

    管理员查看单条申请的完整信息：问卷 JSON、附件列表、脱敏手机号。

    权限：admin 只读。
    """

    applicant = UserSerializer(read_only=True)
    pet = PetProfileSerializer(read_only=True)
    # 问卷答案 JSON（来自 AdoptQuestionnaire.answers_json）
    questionnaire = serializers.SerializerMethodField()
    # 附件列表
    attachments = serializers.SerializerMethodField()
    # 脱敏后的申请人手机号
    applicant_phone_masked = serializers.SerializerMethodField()

    class Meta:
        model = AdoptApplication
        fields = [
            'id', 'applicant', 'pet', 'online_status', 'audit_opinion', 'message',
            'questionnaire', 'attachments', 'applicant_phone_masked', 'created_at',
        ]

    def get_questionnaire(self, obj):
        """
        获取问卷 JSON 答案。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            dict | None: answers_json 内容
        """
        try:
            return obj.questionnaire.answers_json
        except AdoptQuestionnaire.DoesNotExist:
            return None

    def get_attachments(self, obj):
        """
        获取全部附件序列化数据。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            list: 附件字典列表
        """
        return AdoptAttachmentSerializer(obj.attachments.all(), many=True).data

    def get_applicant_phone_masked(self, obj):
        """
        对申请人手机号脱敏：保留前 3 位与后 4 位，中间用 **** 替代。

        参数:
            obj (AdoptApplication): 申请实例
        返回:
            str | None: 脱敏手机号
        """
        phone = getattr(getattr(obj.applicant, 'profile', None), 'phone', None)
        if not phone:
            return None
        phone_str = str(phone).strip()
        if len(phone_str) >= 7:
            return phone_str[:3] + '****' + phone_str[-4:]
        return phone_str[:3] + '****'


class PetProfileUpdateSerializer(PetProfileSerializer):
    """
    宠物档案更新序列化器。

    继承 PetProfileSerializer，额外限制：已领养宠物不可修改 adoption_status 或 is_public。

    权限：admin 可更新。
    """

    def validate(self, attrs):
        """
        更新校验：已领养宠物禁止改公开状态或领养状态。

        参数:
            attrs (dict): 待更新字段
        返回:
            dict: 校验通过的 attrs
        异常:
            ValidationError: 已领养宠物试图修改状态时
        """
        if self.instance and self.instance.adoption_status == 'adopted':
            if 'adoption_status' in attrs or 'is_public' in attrs:
                raise serializers.ValidationError('\u5df2\u9886\u517b\u5ba0\u7269\u4e0d\u53ef\u4fee\u6539\u516c\u5f00\u6216\u9886\u517b\u72b6\u6001')
        return attrs
