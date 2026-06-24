from django.db.models import F, Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

<<<<<<< HEAD
=======
from common.permissions import IsActiveUser
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
from common.user_block import is_blocked
from .models import CommentLike, CommunityComment, CommunityPost, PostFavorite, PostLike
from .serializers import (
    CommunityCommentSerializer,
    CommunityPostSerializer,
    PostFavoriteItemSerializer,
    build_comment_threads,
)


def _is_admin(user):
    return getattr(getattr(user, 'profile', None), 'role', None) == 'admin'


def _can_manage_post(user, post):
    return user.is_authenticated and (post.author_id == user.id or _is_admin(user))


def _collect_subtree_ids(comment):
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
    queryset = CommunityPost.objects.filter(is_deleted=False).select_related('author', 'author__profile')
    serializer_class = CommunityPostSerializer

    def get_permissions(self):
<<<<<<< HEAD
        if self.action in ['list', 'retrieve', 'comments']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
=======
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'comments' and self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsActiveUser()]
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        author_id = self.request.query_params.get('author') or self.request.query_params.get('author_id')
        if category:
            qs = qs.filter(category=category)
        if author_id:
            qs = qs.filter(author_id=author_id)
            if self.request.user.is_authenticated:
                from django.contrib.auth import get_user_model
                author = get_user_model().objects.filter(pk=author_id).first()
                if author and is_blocked(self.request.user, author):
                    return qs.none()
        user = self.request.user
        if user.is_authenticated:
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
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated and is_blocked(user, obj.author):
            raise PermissionDenied('blocked_by_user')
        return obj

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if not _can_manage_post(self.request.user, instance):
            raise PermissionDenied('Not allowed to update this post')
        editable = ('title', 'content', 'category', 'image_urls')
        if any(field in serializer.validated_data for field in editable):
            serializer.save(edited_at=timezone.now())
        else:
            serializer.save()

    def perform_destroy(self, instance):
        if not _can_manage_post(self.request.user, instance):
            raise PermissionDenied('Not allowed to delete this post')
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            return Response(build_comment_threads(post, request))
        if not request.user.is_authenticated:
            raise PermissionDenied('Authentication required')
        if is_blocked(request.user, post.author):
            raise PermissionDenied('blocked_by_user')
        parent_id = request.data.get('parent')
        parent = None
        root_id = None
        if parent_id:
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
        post = self.get_object()
        if request.method == 'POST':
            PostFavorite.objects.get_or_create(post=post, user=request.user)
            return Response({'detail': 'Favorited'})
        PostFavorite.objects.filter(post=post, user=request.user).delete()
        return Response({'detail': 'Favorite removed'})


class MyPostFavoritesView(APIView):
<<<<<<< HEAD
    permission_classes = [permissions.IsAuthenticated]
=======
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

    def get(self, request):
        favorites = (
            PostFavorite.objects.filter(user=request.user, post__is_deleted=False)
            .select_related('post', 'post__author')
            .order_by('-created_at')
        )
        serializer = PostFavoriteItemSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)


class CommunityCommentViewSet(viewsets.GenericViewSet):
    queryset = CommunityComment.objects.filter(is_deleted=False).select_related('post', 'author')
<<<<<<< HEAD
    permission_classes = [permissions.IsAuthenticated]
=======
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

    def destroy(self, request, pk=None):
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
