"""
内容处置联动业务表。【权限】仅 admin 调用。
"""

from cms.models import CmsArticle
from community.models import CommunityPost
from lostfound.models import LostFoundPost


CONTENT_TYPES = [
    ('community_post', 'Community Post'),
    ('cms_article', 'CMS Article'),
    ('lost_found_post', 'Lost/Found Post'),
    ('user', 'User'),
]


def apply_moderation(content_type, content_id, action):
    """同步审核动作到业务表。【权限】admin"""
    # 分支：通过不改业务表
    if action == 'approve':
        return
    # 分支：封禁用户
    if content_type == 'user':
        if action != 'ban':
            raise ValueError('user moderation only supports ban action')
        from accounts.models import UserProfile
        profile = UserProfile.objects.filter(user_id=content_id).first()
        if not profile:
            raise ValueError('user not found')
        profile.status = 1
        profile.save(update_fields=['status', 'updated_at'])
        return
    # 分支：社区帖子 hide/delete 标记删除
    if content_type == 'community_post':
        post = CommunityPost.objects.filter(pk=content_id).first()
        if not post:
            raise ValueError('community_post not found')
        if action in ('hide', 'delete'):
            post.is_deleted = True
            post.save(update_fields=['is_deleted', 'updated_at'])
        return
    # 分支：CMS 文章 hide/delete 改 status=2
    if content_type == 'cms_article':
        article = CmsArticle.objects.filter(pk=content_id).first()
        if not article:
            raise ValueError('cms_article not found')
        if action in ('hide', 'delete'):
            article.status = 2
            article.save(update_fields=['status', 'updated_at'])
        return
    # 分支：失领帖 hide/delete 改 cancelled
    if content_type == 'lost_found_post':
        post = LostFoundPost.objects.filter(pk=content_id).first()
        if not post:
            raise ValueError('lost_found_post not found')
        if action in ('hide', 'delete'):
            post.status = 'cancelled'
            post.save(update_fields=['status', 'updated_at'])
        return
    raise ValueError(f'unsupported content_type: {content_type}')
