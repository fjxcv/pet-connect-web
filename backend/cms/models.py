"""
cms 模块：文章分类、文章（科普/公告/法规/救助案例）、收藏模型。
【权限】visitor 读公开；user 可收藏；admin 增删改。
"""

from django.contrib.auth.models import User
from django.db import models


class CmsCategory(models.Model):
    """
    功能：文章分类（名称、描述、排序、启用/禁用）。
    【权限】visitor/user 读启用；admin 增删改
    """
    STATUS_CHOICES = [(0, 'Disabled'), (1, 'Enabled')]
    # 字段说明：0 禁用，1 启用
    name = models.CharField(max_length=50)
    # 字段说明：分类名称
    description = models.CharField(max_length=200, blank=True, null=True)
    # 字段说明：分类描述
    sort_order = models.IntegerField(default=0)
    # 字段说明：排序
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    # 字段说明：启用状态
    created_at = models.DateTimeField(auto_now_add=True)
    # 字段说明：创建时间

    class Meta:
        db_table = 'cms_category'
        ordering = ['sort_order', 'id']


class CmsArticle(models.Model):
    """
    功能：文章/公告/法规/救助案例（支持置顶、分类、作者、发布时间）。
    【权限】visitor/user 读 status=1；admin 全部
    """
    ARTICLE_TYPE_CHOICES = [
        ('science', 'Science'),
        ('announcement', 'Announcement'),
        ('law', 'Law'),
        ('rescue_case', 'Rescue Case'),
    ]
    # 字段说明：文章类型（science 科普、announcement 公告、law 法规、rescue_case 救助案例）
    STATUS_CHOICES = [(0, 'Draft'), (1, 'Published'), (2, 'Offline')]
    # 字段说明：0 草稿，1 已发布，2 下线
    category = models.ForeignKey(
        CmsCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles'
    )
    # 字段说明：所属分类（可空）
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='cms_articles')
    # 字段说明：作者（管理员）
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPE_CHOICES)
    # 字段说明：类型
    title = models.CharField(max_length=200)
    # 字段说明：标题
    summary = models.CharField(max_length=500, blank=True, null=True)
    # 字段说明：摘要
    content = models.TextField()
    # 字段说明：正文（Markdown）
    cover_url = models.CharField(max_length=500, blank=True, null=True)
    # 字段说明：封面图
    view_count = models.IntegerField(default=0)
    # 字段说明：阅读量
    is_pinned = models.BooleanField(default=False)
    # 字段说明：是否置顶
    sort_weight = models.IntegerField(default=0)
    # 字段说明：排序权重
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    # 字段说明：发布状态
    published_at = models.DateTimeField(blank=True, null=True)
    # 字段说明：发布时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 字段说明：创建时间
    updated_at = models.DateTimeField(auto_now=True)
    # 字段说明：最后更新时间

    class Meta:
        db_table = 'cms_article'
        ordering = ['-is_pinned', '-sort_weight', '-published_at', '-created_at']


class ArticleFavorite(models.Model):
    """
    功能：用户收藏文章（唯一约束 article+user）。
    【权限】user：本人收藏；admin：可看全部
    """
    article = models.ForeignKey(CmsArticle, on_delete=models.CASCADE, related_name='favorites')
    # 字段说明：被收藏的文章
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_favorites')
    # 字段说明：收藏用户
    created_at = models.DateTimeField(auto_now_add=True)
    # 字段说明：收藏时间

    class Meta:
        db_table = 'article_favorite'
        unique_together = [('article', 'user')]

