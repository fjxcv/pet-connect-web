"""
模块说明：community 模块序列化器。

负责社区帖子、评论、收藏等数据的序列化与反序列化，
并在响应中附加当前登录用户的点赞/收藏状态及评论楼层结构。
"""

from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import CommentLike, CommunityComment, CommunityPost, PostFavorite, PostLike


def _display_name(user):
    """
    获取用户对外展示名称：优先昵称，否则回退用户名。

    参数:
        user (User | None): 用户对象，可为空
    返回:
        str: 展示用名称，无用户时返回空字符串
    """
    if not user:
        return ''
    profile = getattr(user, 'profile', None)
    if profile and profile.nickname:
        return profile.nickname
    return user.username


def _infer_root_id(comment):
    """
    推断评论所属评论楼的根评论 ID。

    若评论已存 root_id 则直接返回；否则沿 parent 链向上找到顶层评论。

    参数:
        comment (CommunityComment): 评论实例
    返回:
        int: 根评论的主键 ID
    """
    if comment.root_id:
        return comment.root_id
    node = comment
    while node.parent_id:
        node = node.parent
    return node.id


class CommunityCommentSerializer(serializers.ModelSerializer):
    """
    社区评论序列化器。

    输出单条评论及嵌套回复树，并标注：
    - floor：楼层号（仅顶层评论由 build_comment_threads 注入）
    - is_post_author：是否为楼主
    - is_admin：评论者是否为管理员
    - is_liked：当前登录用户是否已点赞该评论
    - reply_to：回复对象的展示名
    """

    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    floor = serializers.IntegerField(read_only=True, required=False)
    is_post_author = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = CommunityComment
        fields = [
            'id', 'post', 'author', 'parent', 'content', 'like_count', 'created_at',
            'replies', 'floor', 'is_post_author', 'is_admin', 'is_liked', 'reply_to',
        ]
        read_only_fields = ['author', 'like_count', 'created_at']

    def _post_author_id(self):
        """
        从上下文获取帖子作者 ID，用于判断「是否楼主」。

        返回:
            int | None: 帖子作者用户 ID
        """
        post = self.context.get('post')
        if post:
            return post.author_id
        return self.context.get('post_author_id')

    def get_is_post_author(self, obj):
        """
        判断评论作者是否为帖子作者（楼主）。

        参数:
            obj (CommunityComment): 当前评论
        返回:
            bool: 是楼主为 True，否则 False
        """
        author_id = self._post_author_id()
        return author_id and obj.author_id == author_id

    def get_is_admin(self, obj):
        """
        判断评论作者角色是否为管理员 admin。

        参数:
            obj (CommunityComment): 当前评论
        返回:
            bool: 评论者为管理员时为 True
        """
        profile = getattr(obj.author, 'profile', None)
        return bool(profile and profile.role == 'admin')

    def get_is_liked(self, obj):
        """
        判断当前登录用户是否已点赞该评论。

        权限：visitor 未登录时恒为 False；user / admin 登录后按库表查询。

        参数:
            obj (CommunityComment): 当前评论
        返回:
            bool: 已点赞为 True
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False

    def get_reply_to(self, obj):
        """
        获取被回复用户的展示名称（楼中楼场景）。

        参数:
            obj (CommunityComment): 当前评论
        返回:
            str | None: 父评论作者昵称/用户名；顶层评论返回 None
        """
        if not obj.parent_id:
            return None
        parent = obj.parent
        if hasattr(parent, 'author'):
            return _display_name(parent.author)
        return None

    def get_replies(self, obj):
        """
        序列化当前评论楼下的所有楼中楼回复（按时间排序）。

        参数:
            obj (CommunityComment): 当前顶层评论
        返回:
            list: 回复评论的字典列表
        """
        tree = self.context.get('replies_by_root') or {}
        children = tree.get(obj.id, [])
        return CommunityCommentSerializer(
            children,
            many=True,
            context=self.context,
        ).data


def build_comment_threads(post, request):
    """
    构建帖子下的评论线程列表（带楼层号与嵌套回复）。

    流程：
    1. 查询帖子下所有未删除评论
    2. 分离顶层评论与楼中楼，按 root 分组
    3. 为顶层评论编号 floor（从 1 开始）
    4. 序列化并返回完整树形结构

    权限：visitor / user / admin 均可调用（只读展示）；
    is_liked 等字段依赖 request 中是否已登录。

    参数:
        post (CommunityPost): 目标帖子
        request (Request): 当前 HTTP 请求，用于传递登录态
    返回:
        list: 顶层评论列表，每项含 floor 与嵌套 replies
    """
    comments = list(
        CommunityComment.objects.filter(post=post, is_deleted=False)
        .select_related('author', 'author__profile', 'parent', 'parent__author', 'parent__author__profile')
        .order_by('created_at')
    )
    # 顶层评论：无 parent_id
    tops = [c for c in comments if not c.parent_id]
    tops.sort(key=lambda x: x.created_at)
    # 按根评论 ID 聚合楼中楼回复
    replies_by_root = {}
    for c in comments:
        if c.parent_id:
            root_id = _infer_root_id(c)
            replies_by_root.setdefault(root_id, []).append(c)
    for root_id in replies_by_root:
        replies_by_root[root_id].sort(key=lambda x: x.created_at)
    ctx = {
        'request': request,
        'post': post,
        'post_author_id': post.author_id,
        'replies_by_root': replies_by_root,
    }
    result = []
    for floor, top in enumerate(tops, start=1):
        data = CommunityCommentSerializer(top, context=ctx).data
        data['floor'] = floor
        result.append(data)
    return result


class CommunityPostSerializer(serializers.ModelSerializer):
    """
    社区帖子序列化器。

    用于帖子列表、详情及嵌套在收藏项中；
    附加 is_liked、is_favorited、is_edited 等前端展示字段。
    """

    author = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_edited = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = [
            'id', 'author', 'category', 'title', 'content', 'image_urls',
            'like_count', 'comment_count', 'is_deleted', 'created_at', 'updated_at',
            'edited_at', 'is_edited', 'is_liked', 'is_favorited',
        ]
        read_only_fields = ['author', 'like_count', 'comment_count', 'created_at', 'updated_at', 'edited_at']

    def get_is_edited(self, obj):
        """
        判断帖子是否曾被作者编辑过（edited_at 有值即为已编辑）。

        参数:
            obj (CommunityPost): 帖子实例
        返回:
            bool: 已编辑为 True
        """
        return bool(obj.edited_at)

    def get_is_liked(self, obj):
        """
        判断当前登录用户是否已点赞该帖子。

        权限：visitor 未登录恒为 False；user / admin 按库表查询。

        参数:
            obj (CommunityPost): 帖子实例
        返回:
            bool: 已点赞为 True
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False

    def get_is_favorited(self, obj):
        """
        判断当前登录用户是否已收藏该帖子。

        权限：visitor 未登录恒为 False；user / admin 按库表查询。

        参数:
            obj (CommunityPost): 帖子实例
        返回:
            bool: 已收藏为 True
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostFavorite.objects.filter(post=obj, user=request.user).exists()
        return False


class PostFavoriteItemSerializer(serializers.ModelSerializer):
    """
    帖子收藏项序列化器。

    用于「我的收藏」列表，每条记录嵌套完整帖子信息。
    """

    post = CommunityPostSerializer(read_only=True)

    class Meta:
        model = PostFavorite
        fields = ['id', 'created_at', 'post']
