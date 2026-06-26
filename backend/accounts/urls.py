"""
模块说明：accounts 模块 URL 路由。
"""

from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    EmailChangeConfirmView,
    EmailChangeRequestView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    PublicUserProfileView,
    RegisterView,
    UserBlockView,
)
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/<int:pk>/public/', PublicUserProfileView.as_view(), name='public-user-profile'),
    path('users/<int:pk>/block/', UserBlockView.as_view(), name='user-block'),
    path('auth/password/reset-request/', PasswordResetRequestView.as_view()),
    path('auth/password/reset-confirm/', PasswordResetConfirmView.as_view()),
    path('auth/email/change-request/', EmailChangeRequestView.as_view()),
    path('auth/email/change-confirm/', EmailChangeConfirmView.as_view()),
]

