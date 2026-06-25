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
    queryset = PetProfile.objects.all()
    serializer_class = PetProfileSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PetProfileUpdateSerializer
        return PetProfileSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'nearby']:
            return [permissions.AllowAny()]
        if self.action == 'my_pets':
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def get_queryset(self):
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
        """Get pets published by current user via rescue_case."""
        qs = PetProfile.objects.filter(
            rescue_case__reporter=request.user,
        ).select_related('rescue_case')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AdoptApplicationViewSet(viewsets.ModelViewSet):
    queryset = AdoptApplication.objects.select_related('applicant', 'pet', 'auditor', 'offline_verify').all()
    serializer_class = AdoptApplicationSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action in ['create', 'my', 'questionnaire', 'attachments']:
            return [permissions.IsAuthenticated()]
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = self.queryset.prefetch_related('attachments').select_related('questionnaire')
        if self.action == 'my':
            return qs.filter(applicant=self.request.user)
        if self.action == 'retrieve':
            if user_is_admin(self.request.user):
                return qs
            return qs.filter(applicant=self.request.user)
        return qs

    def perform_create(self, serializer):
        pet = serializer.validated_data['pet']
        if pet.adoption_status != 'available':
            raise ValidationError({'pet_id': '\u8be5\u5ba0\u7269\u5f53\u524d\u4e0d\u53ef\u7533\u8bf7\u9886\u517b'})
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
        qs = self.get_queryset()
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='questionnaire')
    def questionnaire(self, request, pk=None):
        app = self.get_object()
        if app.applicant != request.user:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
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
        app = self.get_object()
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
    queryset = AdoptApplication.objects.select_related(
        'applicant', 'applicant__profile', 'pet', 'pet__rescue_case', 'auditor',
    ).prefetch_related('attachments', 'questionnaire').all()
    serializer_class = AdoptApplicationAuditSerializer
    permission_classes = [IsAdminRole]

    def list(self, request):
        qs = self.get_queryset()
        serializer = AdminAdoptApplicationListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def review_detail(self, request, pk=None):
        app = self.get_object()
        return Response(AdoptApplicationReviewDetailSerializer(app).data)

    def update(self, request, pk=None):
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
    queryset = AdoptOfflineVerify.objects.select_related('application').all()
    serializer_class = AdoptOfflineVerifySerializer
    permission_classes = [IsAdminRole]

    def update(self, request, pk=None):
        verify = self.get_object()
        new_status = request.data.get('verify_status', verify.verify_status)
        verify_note = request.data.get('verify_note', verify.verify_note)
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
        if verify.verify_status == 'passed':
            verify.application.online_status = 'approved'
            verify.application.pet.adoption_status = 'adopted'
            verify.application.pet.is_public = False
        elif verify.verify_status == 'failed':
            verify.application.online_status = 'rejected'
            verify.application.pet.adoption_status = 'available'
        verify.application.save()
        verify.application.pet.save()
        return Response(AdoptOfflineVerifySerializer(verify).data)

    def create_for_application(self, request, application_id=None):
        app = AdoptApplication.objects.get(pk=application_id)
        verify, _ = AdoptOfflineVerify.objects.get_or_create(application=app)
        return Response(AdoptOfflineVerifySerializer(verify).data)
