"""
模块说明：api Django Admin 注册。
"""

from django.contrib import admin
from django.urls import include, path
from accounts.models import UserEmailChangeLog, UserPasswordResetLog, UserProfile, UserVerificationCode
from cms.models import ArticleFavorite, CmsArticle, CmsCategory
from community.models import CommentLike, CommunityComment, CommunityPost, PostFavorite, PostLike
from lostfound.models import LostFoundPost
from pets.models import AdoptApplication, AdoptAttachment, AdoptOfflineVerify, AdoptQuestionnaire, PetProfile
from portal.models import PortalCarousel
from rescue.models import RescueCase, RescueStatusLog
from system.models import AiInvocationLog, ContentModeration, OperationLog, PlatformConfig
admin.site.register(UserProfile)
admin.site.register(UserVerificationCode)
admin.site.register(UserEmailChangeLog)
admin.site.register(UserPasswordResetLog)
admin.site.register(PortalCarousel)
admin.site.register(CmsCategory)
admin.site.register(CmsArticle)
admin.site.register(ArticleFavorite)
admin.site.register(LostFoundPost)
admin.site.register(RescueCase)
admin.site.register(RescueStatusLog)
admin.site.register(PetProfile)
admin.site.register(AdoptApplication)
admin.site.register(AdoptQuestionnaire)
admin.site.register(AdoptAttachment)
admin.site.register(AdoptOfflineVerify)
admin.site.register(CommunityPost)
admin.site.register(CommunityComment)
admin.site.register(PostLike)
admin.site.register(PostFavorite)
admin.site.register(CommentLike)
admin.site.register(OperationLog)
admin.site.register(ContentModeration)
admin.site.register(PlatformConfig)
admin.site.register(AiInvocationLog)

