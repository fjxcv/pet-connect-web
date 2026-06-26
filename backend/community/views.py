"""
模块说明：community 模块 API 视图。

提供社区帖子的增删改查、评论、点赞、收藏，
以及评论删除与评论点赞等 HTTP 接口。
"""

from django.db.models import F, Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from common.permissions import IsActiveUser
from common.user_block import is_blocked
from .models import CommentLike, CommunityComment, CommunityPost, PostFavorite, PostLike
from .serializers import (
    CommunityCommentSerializer,
    CommunityPostSerializer,
    PostFavoriteItemSerializer,
    build_comment_threads,
)


def _is_admin(user):
    """
    判断用户是否为管理员 admin。

    参数:
        user (User): 待判断用户
    返回:
        bool: profile.role == 'admin' 时为 True
    """
    return getattr(getattr(user, 'profile', None), 'role', None) == 'admin'


def _can_manage_post(user, post):
    """
    判断用户是否有权管理（编辑/删除）指定帖子。

    权限规则：
    - 帖子作者本人：允许
    - 管理员 admin：允许
    - 其他用户（含 visitor 未登录）：不允许

    参数:
        user (User): 当前操作用户
        post (CommunityPost): 目标帖子
    返回:
        bool: 有管理权限为 True
    """
    return user.is_authenticated and (post.author_id == user.id or _is_admin(user))


def _collect_subtree_ids(comment):
    """
    收集评论及其所有子回复的 ID（广度优先遍历）。

    删除顶层评论时需软删除整棵子树，并相应扣减帖子 comment_count。

    参数:
        comment (CommunityComment): 起始评论（含自身）
    返回:
        list[int]: 子树内所有未删评论的 ID 列表
    """
    ids = [comment.id]
    queue = [comment.id]
    while queue:
        cid = queue.pop(0)
        child_ids = list(
            CommunityComment.objects.filter(parent_id=cid, is_deleted=False).values_list('id', flat=True)
        )
        ids.extend(child_ids)
        queue.extend(child_ids)
    return ids


class CommunityPostViewSet(viewsets.ModelViewSet):
    """
    社区帖子视图集。

    标准 REST：列表、详情、创建、更新、删除（软删）。
    扩展动作：comments（查/发评论）、like（赞/取消）、favorite（藏/取消）。

    权限总览：
    - list / retrieve / GET comments：visitor / user / admin 均可
    - create / update / destroy / POST comments / like / favorite：user / admin 且账号未封禁（IsActiveUser）
    """

    queryset = CommunityPost.objects.filter(is_deleted=False).select_related('author', 'author__profile')
    serializer_class = CommunityPostSerializer

    def get_permissions(self):
        """
        按动作动态设置接口权限。

        返回:
            list: 权限类实例列表
        """
        # 浏览帖子列表、详情及只读查看评论：游客也可访问
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'comments' and self.request.method == 'GET':
            return [permissions.AllowAny()]
        # 发帖、改帖、删帖、评论、点赞、收藏：须登录且账号正常
        return [permissions.IsAuthenticated(), IsActiveUser()]

    def get_queryset(self):
        """
        构建帖子查询集：支持分类、作者、搜索、排序及拉黑过滤。

        参数（query_params）:
            category: 按分类筛选
            author / author_id: 按作者筛选；若查看拉黑用户主页则返回空
            q / search: 标题或正文关键词搜索
            ordering: latest（默认）或 likes 按点赞数排序

        权限相关逻辑：
        - 登录用户自动排除「拉黑了自己」的作者的帖子
        - 按作者筛选时若双方存在拉黑关系则返回空结果

        返回:
            QuerySet: 过滤后的帖子查询集
        """
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        author_id = self.request.query_params.get('author') or self.request.query_params.get('author_id')
        if category:
            qs = qs.filter(category=category)
        if author_id:
            qs = qs.filter(author_id=author_id)
            # 登录用户查看某作者帖子时，校验是否被该作者拉黑
            if self.request.user.is_authenticated:
                from django.contrib.auth import get_user_model
                author = get_user_model().objects.filter(pk=author_id).first()
                if author and is_blocked(self.request.user, author):
                    return qs.none()
        user = self.request.user
        if user.is_authenticated:
            # 排除拉黑当前用户的用户所发的帖子
            blocked_author_ids = list(
                user.blocked_by.values_list('blocker_id', flat=True)
            )
            if blocked_author_ids:
                qs = qs.exclude(author_id__in=blocked_author_ids)
        search_q = (self.request.query_params.get('q') or self.request.query_params.get('search') or '').strip()
        if search_q:
            qs = qs.filter(Q(title__icontains=search_q) | Q(content__icontains=search_q))
        ordering = self.request.query_params.get('ordering', 'latest')
        if ordering == 'likes':
            qs = qs.order_by('-like_count', '-created_at')
        else:
            qs = qs.order_by('-created_at')
        return qs

    def get_object(self):
        """
        获取单条帖子；若作者拉黑了当前用户则拒绝访问。

        返回:
            CommunityPost: 帖子实例
        异常:
            PermissionDenied: 存在拉黑关系时
        """
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated and is_blocked(user, obj.author):
            raise PermissionDenied('blocked_by_user')
        return obj

    def perform_create(self, serializer):
        """
        创建帖子：作者自动设为当前登录用户。

        权限：user / admin（由 get_permissions 保证已登录）。

        参数:
            serializer: 已通过校验的帖子序列化器
        """
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """
        更新帖子：仅作者或 admin 可改；修改内容类字段时记录 edited_at。

        权限：帖子作者或 admin，否则 PermissionDenied。

        参数:
            serializer: 含待更新字段的序列化器
        """
        instance = self.get_object()
        if not _can_manage_post(self.request.user, instance):
            raise PermissionDenied('Not allowed to update this post')
        editable = ('title', 'content', 'category', 'image_urls')
        # 若改了标题/正文等，记录编辑时间
        if any(field in serializer.validated_data for field in editable):
            serializer.save(edited_at=timezone.now())
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        软删除帖子：仅作者或 admin 可删，将 is_deleted 置 True。

        权限：帖子作者或 admin，否则 PermissionDenied。

        参数:
            instance (CommunityPost): 待删除帖子
        """
        if not _can_manage_post(self.request.user, instance):
            raise PermissionDenied('Not allowed to delete this post')
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        """
        帖子评论接口：GET 拉取评论树，POST 发表评论或楼中楼回复。

        权限：
        - GET：visitor / user / admin
        - POST：user / admin，且不能与楼主存在拉黑关系

        参数:
            request: GET 无体；POST 含 content、可选 parent（父评论 ID）
            pk: 帖子 ID
        返回:
            Response: GET 为评论线程列表；POST 为 201 + 新评论数据
        """
        post = self.get_object()
        if request.method == 'GET':
            return Response(build_comment_threads(post, request))
        if not request.user.is_authenticated:
            raise PermissionDenied('Authentication required')
        # 被楼主拉黑的用户不能在其帖子下评论
        if is_blocked(request.user, post.author):
            raise PermissionDenied('blocked_by_user')
        parent_id = request.data.get('parent')
        parent = None
        root_id = None
        if parent_id:
            # 楼中楼：校验父评论属于本帖且未删除
            parent = CommunityComment.objects.filter(
                pk=parent_id, post=post, is_deleted=False,
            ).select_related('parent').first()
            if not parent:
                raise NotFound('Parent comment not found')
            root_id = parent.root_id or parent.id
        comment = CommunityComment.objects.create(
            post=post,
            author=request.user,
            parent=parent,
            root_id=root_id,
            content=request.data['content'],
        )
        CommunityPost.objects.filter(pk=post.pk).update(comment_count=F('comment_count') + 1)
        threads = build_comment_threads(post, request)
        created = next((t for t in threads if t['id'] == comment.id), None)
        # 新评论可能是楼中楼，需在 replies 中查找
        if not created and parent_id:
            for thread in threads:
                for reply in thread.get('replies', []):
                    if reply['id'] == comment.id:
                        created = reply
                        break
        if not created:
            created = CommunityCommentSerializer(
                comment,
                context={'request': request, 'post': post, 'post_author_id': post.author_id},
            ).data
        return Response(created, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'], url_path='like')
    def like(self, request, pk=None):
        """
        帖子点赞 / 取消点赞。

        权限：user / admin（须登录）。
        POST 点赞（幂等，已赞不重复加计数）；DELETE 取消点赞。

        参数:
            request: POST 或 DELETE
            pk: 帖子 ID
        返回:
            Response: 操作结果提示
        """
        post = self.get_object()
        if request.method == 'POST':
            _, created = PostLike.objects.get_or_create(post=post, user=request.user)
            if created:
                CommunityPost.objects.filter(pk=post.pk).update(like_count=F('like_count') + 1)
            return Response({'detail': 'Liked'})
        deleted, _ = PostLike.objects.filter(post=post, user=request.user).delete()
        if deleted:
            CommunityPost.objects.filter(pk=post.pk, like_count__gt=0).update(like_count=F('like_count') - 1)
        return Response({'detail': 'Like removed'})

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """
        帖子收藏 / 取消收藏。

        权限：user / admin（须登录）。

        参数:
            request: POST 收藏或 DELETE 取消
            pk: 帖子 ID
        返回:
            Response: 操作结果提示
        """
        post = self.get_object()
        if request.method == 'POST':
            PostFavorite.objects.get_or_create(post=post, user=request.user)
            return Response({'detail': 'Favorited'})
        PostFavorite.objects.filter(post=post, user=request.user).delete()
        return Response({'detail': 'Favorite removed'})


class MyPostFavoritesView(APIView):
    """
    当前用户帖子收藏列表接口。

    GET：返回当前用户收藏的所有未删除帖子。

    权限：user / admin（须登录且账号未封禁）。
    """

    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def get(self, request):
        """
        查询我的收藏列表，按收藏时间倒序。

        参数:
            request: 当前登录用户
        返回:
            Response: PostFavoriteItemSerializer 列表
        """
        favorites = (
            PostFavorite.objects.filter(user=request.user, post__is_deleted=False)
            .select_related('post', 'post__author')
            .order_by('-created_at')
        )
        serializer = PostFavoriteItemSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)


class CommunityCommentViewSet(viewsets.GenericViewSet):
    """
    社区评论视图集（删除与点赞）。

    不提供列表/创建（创建走帖子的 comments 动作）；
    支持删除整条评论子树及评论点赞/取消。

    权限：user / admin（须登录且未封禁）。
    删除评论：评论作者、帖子作者或 admin 可删。
    """

    queryset = CommunityComment.objects.filter(is_deleted=False).select_related('post', 'author')
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def destroy(self, request, pk=None):
        """
        软删除评论及其所有楼中楼回复。

        权限（满足其一即可）：
        - 评论作者本人
        - 帖子作者（楼主）
        - 管理员 admin

        参数:
            request: 当前登录用户
            pk: 评论 ID
        返回:
            Response: 204 无内容
        """
        comment = self.get_object()
        post = comment.post
        can_delete = (
            comment.author_id == request.user.id
            or post.author_id == request.user.id
            or _is_admin(request.user)
        )
        if not can_delete:
            raise PermissionDenied('Not allowed to delete this comment')
        ids = _collect_subtree_ids(comment)
        CommunityComment.objects.filter(pk__in=ids).update(is_deleted=True)
        CommunityPost.objects.filter(pk=post.pk, comment_count__gte=len(ids)).update(
            comment_count=F('comment_count') - len(ids),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='like')
    def like(self, request, pk=None):
        """
        评论点赞 / 取消点赞。

        权限：user / admin（须登录）。

        参数:
            request: POST 点赞或 DELETE 取消
            pk: 评论 ID
        返回:
            Response: 操作结果提示
        """
        comment = self.get_object()
        if request.method == 'POST':
            _, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
            if created:
                CommunityComment.objects.filter(pk=comment.pk).update(like_count=F('like_count') + 1)
            return Response({'detail': 'Liked'})
        deleted, _ = CommentLike.objects.filter(comment=comment, user=request.user).delete()
        if deleted:
            CommunityComment.objects.filter(pk=comment.pk, like_count__gt=0).update(
                like_count=F('like_count') - 1,
            )
        return Response({'detail': 'Like removed'})
