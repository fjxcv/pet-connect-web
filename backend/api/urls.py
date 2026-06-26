"""
模块说明：api 模块 URL 路由。
"""

from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from common.views import UploadView
urlpatterns = [
    path('', include('accounts.urls')),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('uploads/', UploadView.as_view(), name='uploads'),
    path('portal/', include('portal.urls')),
    path('cms/', include('cms.urls')),
    path('lost-found/', include('lostfound.urls')),
    path('rescue/', include('rescue.urls')),
    path('pets/', include('pets.urls')),
    path('adopt/', include('pets.adopt_urls')),
    path('community/', include('community.urls')),
    path('', include('system.urls')),
]

