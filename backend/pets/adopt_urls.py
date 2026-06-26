"""
模块说明：源码：backend/pets/adopt_urls.py
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    AdminAdoptApplicationViewSet,
    AdminOfflineVerifyViewSet,
    AdoptApplicationViewSet,
)
adopt_router = DefaultRouter()
adopt_router.register(r'applications', AdoptApplicationViewSet, basename='adopt-application')
admin_adopt = AdminAdoptApplicationViewSet.as_view({'put': 'update', 'patch': 'update'})
admin_adopt_list = AdminAdoptApplicationViewSet.as_view({'get': 'list'})
admin_adopt_review = AdminAdoptApplicationViewSet.as_view({'get': 'review_detail'})
admin_verify = AdminOfflineVerifyViewSet.as_view({'put': 'update', 'patch': 'update'})
urlpatterns = [
    path('applications/admin/', admin_adopt_list, name='admin-adopt-list'),
] + adopt_router.urls + [
    path('applications/<int:pk>/audit/', admin_adopt, name='admin-adopt-audit'),
    path('applications/<int:pk>/review-detail/', admin_adopt_review, name='admin-adopt-review-detail'),
    path('offline-verify/<int:pk>/', admin_verify, name='admin-offline-verify'),
]

