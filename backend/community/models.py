"""
模块说明：community 模块数据模型（ORM）。

本模块负责社区互动相关的持久化数据，涵盖：
- 社区帖子（发布、分类、软删除、编辑标记）
- 帖子评论（支持楼中楼回复）
- 帖子点赞、收藏、评论点赞
"""

from django.contrib.auth.models import User
from django.db import models


class CommunityPost(models.Model):
    """
    社区帖子表。

    用户可在社区发布图文帖子，支持分类筛选、点赞计数、评论计数及软删除；
    删除帖子时不物理删行，仅将 is_deleted 置为 True。
    """

    # 帖子分类枚举
    CATEGORY_CHOICES = [
        ('general', 'General'),               # 综合讨论
        ('rescue_share', 'Rescue Share'),     # 救助分享
        ('help_request', 'Help Request'),     # 求助
        ('pet_experience', 'Pet Experience'), # 养宠经验
    ]

    # 发帖作者
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    # 帖子分类
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    # 帖子标题
    title = models.CharField(max_length=200)
    # 帖子正文内容
    content = models.TextField()
    # 配图 URL 列表，JSON 数组格式存储
    image_urls = models.JSONField(default=list, blank=True)
    # 点赞总数（冗余字段，便于列表排序展示）
    like_count = models.IntegerField(default=0)
    # 评论总数（冗余字段，含楼中楼回复）
    comment_count = models.IntegerField(default=0)
    # 软删除标记，True 表示帖子已删除不再对外展示
    is_deleted = models.BooleanField(default=False)
    # 帖子创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 帖子最后更新时间（含非内容字段变更）
    updated_at = models.DateTimeField(auto_now=True)
    # 内容最后编辑时间，有值表示作者曾修改过标题/正文等
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'community_post'
        # 默认按创建时间倒序，最新帖子在前
        ordering = ['-created_at']


class CommunityComment(models.Model):
    """
    社区评论表。

    支持两层结构：顶层评论（楼层）与楼中楼回复。
    - parent：直接回复的父评论，顶层评论 parent 为空
    - root：所属评论楼的根评论 ID，便于聚合同一楼内的所有回复
    """

    # 所属帖子
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    # 评论作者
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    # 直接父评论，顶层评论为空
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies'
    )
    # 评论楼根节点，顶层评论的 root 为空（自身即为根）
    root = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='thread_replies'
    )
    # 评论正文
    content = models.TextField()
    # 点赞总数
    like_count = models.IntegerField(default=0)
    # 软删除标记
    is_deleted = models.BooleanField(default=False)
    # 评论创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_comment'
        # 同一帖子内按时间正序排列评论
        ordering = ['created_at']


class PostLike(models.Model):
    """
    帖子点赞记录表。

    同一用户对同一帖子只能点赞一次（唯一约束），
    点赞/取消点赞时同步更新 CommunityPost.like_count。
    """

    # 被点赞的帖子
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    # 点赞用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    # 点赞时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_like'
        # 防止同一用户对同一帖子重复点赞
        unique_together = [('post', 'user')]


class PostFavorite(models.Model):
    """
    帖子收藏记录表。

    登录用户可将感兴趣的帖子加入收藏，便于在个人收藏列表中回看。
    """

    # 被收藏的帖子
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='favorites')
    # 收藏用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_favorites')
    # 收藏时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_favorite'
        # 防止同一用户对同一帖子重复收藏
        unique_together = [('post', 'user')]


class CommentLike(models.Model):
    """
    评论点赞记录表。

    登录用户可对评论点赞，同一用户对同一评论只能点赞一次。
    """

    # 被点赞的评论
    comment = models.ForeignKey(CommunityComment, on_delete=models.CASCADE, related_name='likes')
    # 点赞用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    # 点赞时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment_like'
        # 防止同一用户对同一评论重复点赞
        unique_together = [('comment', 'user')]
