from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import UserSerializer
from pets.models import AdoptApplication, AdoptAttachment, AdoptOfflineVerify, AdoptQuestionnaire, PetProfile


class PetProfileSerializer(serializers.ModelSerializer):
    rescue_case_address = serializers.SerializerMethodField()
    rescue_case_appearance = serializers.SerializerMethodField()
    size_category_display = serializers.SerializerMethodField()
<<<<<<< HEAD
=======
    rescue_case_latitude = serializers.SerializerMethodField()
    rescue_case_longitude = serializers.SerializerMethodField()
    distance_km = serializers.FloatField(read_only=True)
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

    class Meta:
        model = PetProfile
        fields = '__all__'

    def get_rescue_case_address(self, obj):
<<<<<<< HEAD
=======
        if obj.location_text:
            return obj.location_text
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        if obj.rescue_case:
            return obj.rescue_case.discover_address
        return None

    def get_rescue_case_appearance(self, obj):
        if obj.rescue_case:
            return obj.rescue_case.appearance
        return None

    def get_size_category_display(self, obj):
        return obj.get_size_category_display() if obj.size_category else None

<<<<<<< HEAD
=======
    def get_rescue_case_latitude(self, obj):
        if obj.rescue_case:
            return obj.rescue_case.discover_latitude
        return None

    def get_rescue_case_longitude(self, obj):
        if obj.rescue_case:
            return obj.rescue_case.discover_longitude
        return None

    def validate(self, attrs):
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

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

class AdoptApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    pet = PetProfileSerializer(read_only=True)
    pet_id = serializers.PrimaryKeyRelatedField(
        queryset=PetProfile.objects.all(), source='pet', write_only=True
    )
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
        try:
            return obj.offline_verify.verify_status
        except AdoptOfflineVerify.DoesNotExist:
            return None

    def get_verify_note(self, obj):
        try:
            return obj.offline_verify.verify_note
        except AdoptOfflineVerify.DoesNotExist:
            return None

    def validate(self, attrs):
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
    class Meta:
        model = AdoptQuestionnaire
        fields = ['id', 'application', 'answers_json', 'submitted_at']
        read_only_fields = ['application', 'submitted_at']


class AdoptAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptAttachment
        fields = ['id', 'application', 'file_type', 'file_url', 'file_size', 'uploaded_at']
        read_only_fields = ['application', 'uploaded_at']

    def validate_file_size(self, value):
        if value <= 0:
            raise serializers.ValidationError('File size must be greater than 0')
        return value


class AdoptOfflineVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptOfflineVerify
        fields = ['id', 'application', 'verify_status', 'verify_note', 'verifier', 'verified_at']
        read_only_fields = ['application', 'verifier', 'verified_at']


class AdminAdoptApplicationListSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    pet = PetProfileSerializer(read_only=True)
    has_questionnaire = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = AdoptApplication
        fields = [
            'id', 'applicant', 'pet', 'online_status', 'audit_opinion', 'message',
            'created_at', 'has_questionnaire', 'attachment_count',
        ]

    def get_has_questionnaire(self, obj):
        try:
            obj.questionnaire
            return True
        except AdoptQuestionnaire.DoesNotExist:
            return False

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class AdoptApplicationAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptApplication
        fields = ['online_status', 'audit_opinion']

    def validate(self, attrs):
        online_status = attrs.get('online_status')
        audit_opinion = attrs.get('audit_opinion', '')
        if online_status == 'rejected' and not audit_opinion.strip():
            raise serializers.ValidationError({'audit_opinion': '\u62d2\u7edd\u65f6\u5fc5\u987b\u586b\u5199\u9a73\u56de\u539f\u56e0'})
        return attrs

    def update(self, instance, validated_data):
        instance.online_status = validated_data.get('online_status', instance.online_status)
        instance.audit_opinion = validated_data.get('audit_opinion', instance.audit_opinion)
        instance.auditor = self.context['request'].user
        instance.audited_at = timezone.now()
        instance.save()
        if instance.online_status == 'approved':
            instance.pet.adoption_status = 'adopted'
            instance.pet.is_public = False
            instance.pet.save(update_fields=['adoption_status', 'is_public', 'updated_at'])
        elif instance.online_status == 'rejected':
            if not AdoptApplication.objects.filter(pet=instance.pet, online_status__in=['pending', 'approved']).exclude(pk=instance.pk).exists():
                instance.pet.adoption_status = 'available'
                instance.pet.save(update_fields=['adoption_status', 'updated_at'])
        return instance


class AdoptApplicationReviewDetailSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    pet = PetProfileSerializer(read_only=True)
    questionnaire = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    applicant_phone_masked = serializers.SerializerMethodField()

    class Meta:
        model = AdoptApplication
        fields = [
            'id', 'applicant', 'pet', 'online_status', 'audit_opinion', 'message',
            'questionnaire', 'attachments', 'applicant_phone_masked', 'created_at',
        ]

    def get_questionnaire(self, obj):
        try:
            return obj.questionnaire.answers_json
        except AdoptQuestionnaire.DoesNotExist:
            return None

    def get_attachments(self, obj):
        return AdoptAttachmentSerializer(obj.attachments.all(), many=True).data

    def get_applicant_phone_masked(self, obj):
        phone = getattr(getattr(obj.applicant, 'profile', None), 'phone', None)
        if not phone:
            return None
        phone_str = str(phone).strip()
        if len(phone_str) >= 7:
            return phone_str[:3] + '****' + phone_str[-4:]
        return phone_str[:3] + '****'


class PetProfileUpdateSerializer(PetProfileSerializer):
    def validate(self, attrs):
        if self.instance and self.instance.adoption_status == 'adopted':
            if 'adoption_status' in attrs or 'is_public' in attrs:
                raise serializers.ValidationError('\u5df2\u9886\u517b\u5ba0\u7269\u4e0d\u53ef\u4fee\u6539\u516c\u5f00\u6216\u9886\u517b\u72b6\u6001')
        return attrs
