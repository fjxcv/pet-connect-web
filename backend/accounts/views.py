from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.user_block import is_blocked
from community.models import CommunityPost
from community.serializers import CommunityPostSerializer
from lostfound.models import LostFoundPost
from lostfound.serializers import LostFoundPostSerializer

from .models import UserBlock
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .admin_utils import sync_admin_profile_role
from .serializers import (
    EmailChangeConfirmSerializer,
    EmailChangeRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)
<<<<<<< HEAD
from .serializers import create_verification_code
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        profile = getattr(user, 'profile', None)
        token['username'] = user.username
        token['role'] = profile.role if profile else 'user'
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        sync_admin_profile_role(self.user)
        data['user'] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    def get(self, request):
        sync_admin_profile_role(request.user)
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        profile = user.profile
        data = serializer.validated_data
        if 'email' in data:
            user.email = data['email']
            user.save(update_fields=['email'])
        for field in ['nickname', 'phone', 'avatar_url', 'address']:
            if field in data:
                setattr(profile, field, data[field])
        profile.save()
        return Response(UserSerializer(user).data)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification code sent'})


<<<<<<< HEAD
class EmailRegistrationCodeRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        # prevent requesting code for an already-registered email
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            create_verification_code(email, 'registration')
        except ValidationError as e:
            return Response({'detail': e.detail}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception:
            return Response({'detail': 'Failed to send verification email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': 'Verification code sent'})


=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset successful'})


class EmailChangeRequestView(APIView):
    def post(self, request):
        serializer = EmailChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response({'detail': 'Verification code sent to new email'})


class EmailChangeConfirmView(APIView):
    def post(self, request):
        serializer = EmailChangeConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response(UserSerializer(request.user).data)


User = get_user_model()


class PublicUserProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
        profile = getattr(user, 'profile', None)
<<<<<<< HEAD
        if profile and profile.status == 1:
            return Response({'detail': 'User is banned'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated and is_blocked(request.user, user):
            return Response({'detail': 'blocked_by_user'}, status=status.HTTP_403_FORBIDDEN)
        posts = CommunityPost.objects.filter(author=user, is_deleted=False).order_by('-created_at')[:20]
        pet_posts = CommunityPost.objects.filter(
            author=user, is_deleted=False, category='pet_experience',
        ).order_by('-created_at')[:20]
        lost_posts = LostFoundPost.objects.filter(
            publisher=user, status='searching',
        ).order_by('-created_at')[:20]
=======
        is_banned = bool(profile and profile.status == 1)
        is_blocked_by_me = False
        if request.user.is_authenticated and request.user.pk != user.pk:
            is_blocked_by_me = UserBlock.objects.filter(blocker=request.user, blocked=user).exists()
        if request.user.is_authenticated and is_blocked(request.user, user):
            return Response({'detail': 'blocked_by_user'}, status=status.HTTP_403_FORBIDDEN)
        posts = CommunityPost.objects.none()
        pet_posts = CommunityPost.objects.none()
        lost_posts = LostFoundPost.objects.none()
        if not is_banned:
            posts = CommunityPost.objects.filter(author=user, is_deleted=False).order_by('-created_at')[:20]
            pet_posts = CommunityPost.objects.filter(
                author=user, is_deleted=False, category='pet_experience',
            ).order_by('-created_at')[:20]
            lost_posts = LostFoundPost.objects.filter(
                publisher=user, status='searching',
            ).order_by('-created_at')[:20]
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        ctx = {'request': request}
        return Response({
            'id': user.id,
            'username': user.username,
            'nickname': profile.nickname if profile else None,
            'avatar_url': profile.avatar_url if profile else None,
            'role': profile.role if profile else 'user',
<<<<<<< HEAD
=======
            'is_banned': is_banned,
            'is_blocked_by_me': is_blocked_by_me,
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
            'joined_at': profile.created_at if profile else None,
            'community_posts': CommunityPostSerializer(posts, many=True, context=ctx).data,
            'pet_experience_posts': CommunityPostSerializer(pet_posts, many=True, context=ctx).data,
            'lost_found_posts': LostFoundPostSerializer(lost_posts, many=True).data,
        })


class UserBlockView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.pk == pk:
            return Response({'detail': 'Cannot block yourself'}, status=status.HTTP_400_BAD_REQUEST)
        blocked_user = get_object_or_404(User, pk=pk)
        UserBlock.objects.get_or_create(blocker=request.user, blocked=blocked_user)
        return Response({'detail': 'User blocked'})

    def delete(self, request, pk):
        UserBlock.objects.filter(blocker=request.user, blocked_id=pk).delete()
        return Response({'detail': 'User unblocked'})
