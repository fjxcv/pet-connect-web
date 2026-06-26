"""
system 路由：后台与 AI。
将后台管理相关的 API 端点映射到对应的 DRF 视图集
将 AI 相关的单独视图映射到具体路径
最终生成 urlpatterns 供 Django 主路由引用
"""

from django.urls import path

from rest_framework.routers import DefaultRouter



from .views import (

    AdminAiLogViewSet,

    AdminConfigViewSet,

    AdminDashboardView,

    AdminModerationViewSet,

    AdminOperationLogViewSet,

    AdminUserViewSet,

    AiAdoptCopyView,

    AiBreedDetectView,

    AiQaView,

)



admin_router = DefaultRouter()

# 注册后台管理员接口，以下路由仅对 admin 角色开放
admin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

admin_router.register(r'admin/moderation', AdminModerationViewSet, basename='admin-moderation')

admin_router.register(r'admin/config', AdminConfigViewSet, basename='admin-config')

admin_router.register(r'admin/operation-logs', AdminOperationLogViewSet, basename='admin-operation-logs')

admin_router.register(r'admin/ai-logs', AdminAiLogViewSet, basename='admin-ai-logs')



admin_user_update = AdminUserViewSet.as_view({'patch': 'partial_update'})



urlpatterns = [

    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),

    path('admin/users/<int:pk>/', admin_user_update, name='admin-user-update'),

    # AI 接口对登录用户开放，实际请求也会验证用户身份与配额
    path('ai/breed-detect/', AiBreedDetectView.as_view()),

    path('ai/adopt-copy/', AiAdoptCopyView.as_view()),

    path('ai/qa/', AiQaView.as_view()),

] + admin_router.urls

