import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { authAPI, communityAPI, usersAPI } from '../api/api';
import CommentThread from '../components/community/CommentThread';
import ConfirmDeleteModal from '../components/ConfirmDeleteModal';
import { POST_CATEGORIES } from '../constants/site';
import { isAdminUser } from '../components/AdminRoute';
import { useAuthPrompt } from '../context/AuthPromptContext';

const CommunityPostDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [replyTarget, setReplyTarget] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState({ visible: false, message: '', onConfirm: null });
  const [deleteLoading, setDeleteLoading] = useState(false);

  const fetchPost = useCallback(async () => {
    const response = await communityAPI.getPost(id);
    setPost(response.data);
  }, [id]);

  const fetchComments = useCallback(async () => {
    const response = await communityAPI.getComments(id);
    setComments(response.data);
  }, [id]);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const me = localStorage.getItem('token')
          ? await authAPI.getProfile().catch(() => null)
          : null;
        if (me) setCurrentUser(me.data);
        await Promise.all([fetchPost(), fetchComments()]);
      } catch (err) {
        const detail = err.response?.data?.detail;
        if (err.response?.status === 403 && detail === 'blocked_by_user') {
          setError('对方已将你拉黑，无法查看该帖子');
        } else {
          setError('帖子不存在或加载失败。');
        }
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [fetchPost, fetchComments]);

  const { requireAuth } = useAuthPrompt();

  const canManagePost = post && currentUser && (
    post.author?.id === currentUser.id || isAdminUser(currentUser)
  );

  const handleLike = async () => {
    if (!requireAuth()) return;
    setActionLoading(true);
    try {
      if (post.is_liked) {
        await communityAPI.unlikePost(id);
        setPost((p) => ({ ...p, is_liked: false, like_count: Math.max(0, p.like_count - 1) }));
      } else {
        await communityAPI.likePost(id);
        setPost((p) => ({ ...p, is_liked: true, like_count: p.like_count + 1 }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleFavorite = async () => {
    if (!requireAuth()) return;
    setActionLoading(true);
    try {
      if (post.is_favorited) {
        await communityAPI.unfavoritePost(id);
        setPost((p) => ({ ...p, is_favorited: false }));
      } else {
        await communityAPI.favoritePost(id);
        setPost((p) => ({ ...p, is_favorited: true }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const closeDeleteDialog = () => {
    setDeleteDialog({ visible: false, message: '', onConfirm: null });
  };

  const handleConfirmDelete = async () => {
    if (!deleteDialog.onConfirm) return;
    setDeleteLoading(true);
    try {
      await deleteDialog.onConfirm();
      closeDeleteDialog();
    } catch (err) {
      setError(err.response?.data?.detail || '删除失败');
      console.error(err);
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleDeletePost = () => {
    setError(null);
    setDeleteDialog({
      visible: true,
      message: '确定删除该帖子？删除后内容无法恢复',
      onConfirm: async () => {
        await communityAPI.deletePost(id);
        navigate('/community');
      },
    });
  };

  const handleBlockAuthor = async () => {
    if (!post?.author?.id || !window.confirm('确定拉黑该用户？')) return;
    try {
      await usersAPI.blockUser(post.author.id);
      alert('已拉黑');
      navigate('/community');
    } catch (err) {
      alert('操作失败');
    }
  };

  const submitComment = async (content, parentId = null) => {
    await communityAPI.addComment(id, { content: content.trim(), parent: parentId });
    await fetchComments();
    setPost((p) => ({ ...p, comment_count: p.comment_count + 1 }));
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!requireAuth()) return;
    if (!commentText.trim()) return;
    setSubmittingComment(true);
    try {
      await submitComment(commentText, null);
      setCommentText('');
    } catch (err) {
      const detail = err.response?.data?.detail;
      alert(detail === 'blocked_by_user' ? '你已被楼主拉黑，无法评论' : '评论失败');
      console.error(err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleSubmitReply = async () => {
    if (!requireAuth() || !replyTarget || !replyText.trim()) return;
    setSubmittingComment(true);
    try {
      await submitComment(replyText, replyTarget.id);
      setReplyText('');
      setReplyTarget(null);
    } catch (err) {
      const detail = err.response?.data?.detail;
      alert(detail === 'blocked_by_user' ? '你已被楼主拉黑，无法评论' : '回复失败');
      console.error(err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleCommentLike = async (comment) => {
    if (!requireAuth()) return;
    try {
      if (comment.is_liked) {
        await communityAPI.unlikeComment(comment.id);
      } else {
        await communityAPI.likeComment(comment.id);
      }
      await fetchComments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCommentDelete = (comment) => {
    setError(null);
    setDeleteDialog({
      visible: true,
      message: '确定删除该评论？其子回复将一并删除',
      onConfirm: async () => {
        await communityAPI.deleteComment(comment.id);
        await fetchComments();
        await fetchPost();
      },
    });
  };

  const handleReplyTarget = (comment) => {
    if (!requireAuth()) return;
    setReplyTarget(comment);
    setReplyText('');
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="text-center">
        <div className="alert alert-danger">{error || '未找到'}</div>
        <Link to="/community" className="btn btn-outline-secondary">返回社区</Link>
      </div>
    );
  }

  const authorName = post.author?.profile?.nickname || post.author?.username;

  return (
    <div className="py-3">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/community">社区交流</Link></li>
          <li className="breadcrumb-item active">{post.title}</li>
        </ol>
      </nav>

      <article className="card shadow-sm mb-4">
        <div className="card-body">
          <div className="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-2">
            <span className="badge bg-success">{POST_CATEGORIES[post.category] || post.category}</span>
            {canManagePost && (
              <div className="d-flex gap-2">
                <Link to={`/community/${id}/edit`} className="btn btn-sm btn-outline-primary">编辑</Link>
                <button type="button" className="btn btn-sm btn-outline-danger" onClick={handleDeletePost}>
                  删除
                </button>
              </div>
            )}
          </div>
          <h2 className="mb-2">{post.title}</h2>
          <div className="text-muted small mb-2">
            <Link to={`/users/${post.author?.id}`} className="text-decoration-none">{authorName}</Link>
            <span className="mx-1">·</span>
            发布于 {new Date(post.created_at).toLocaleString()}
            {post.edited_at && (
              <>
                <span className="mx-1">·</span>
                最后编辑于 {new Date(post.edited_at).toLocaleString()}
              </>
            )}
          </div>
          <div className="post-content text-start" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
            {post.content}
          </div>

          {post.image_urls?.length > 0 && (
            <div className="row mt-3">
              {post.image_urls.map((url) => (
                <div key={url} className="col-md-4 mb-2">
                  <img src={url} alt="" className="img-fluid rounded" />
                </div>
              ))}
            </div>
          )}

          <div className="d-flex flex-wrap justify-content-center gap-2 mt-4 pt-3 border-top">
            <button
              type="button"
              className={`btn btn-sm ${post.is_liked ? 'btn-danger' : 'btn-outline-danger'}`}
              onClick={handleLike}
              disabled={actionLoading}
            >
              <i className="fas fa-heart me-1" />
              {post.like_count}
            </button>
            <button
              type="button"
              className={`btn btn-sm ${post.is_favorited ? 'btn-warning' : 'btn-outline-warning'}`}
              onClick={handleFavorite}
              disabled={actionLoading}
            >
              <i className="fas fa-star me-1" />
              {post.is_favorited ? '已收藏' : '收藏'}
            </button>
            {currentUser && post.author?.id !== currentUser.id && (
              <button type="button" className="btn btn-sm btn-outline-secondary" onClick={handleBlockAuthor}>
                拉黑作者
              </button>
            )}
          </div>
        </div>
      </article>

      <div className="card shadow-sm">
        <div className="card-header bg-white">
          <h5 className="mb-0"><i className="fas fa-comments me-2" />评论 ({post.comment_count})</h5>
        </div>
        <div className="card-body">
          <form onSubmit={handleCommentSubmit} className="mb-4 comment-compose-form">
            <textarea
              className="form-control comment-compose-input"
              rows={3}
              placeholder="写下你的评论..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
            />
            <button type="submit" className="btn btn-success btn-sm comment-compose-submit" disabled={submittingComment}>
              {submittingComment ? '提交中...' : '发表评论'}
            </button>
          </form>

          <CommentThread
            comments={comments}
            post={post}
            currentUser={currentUser}
            replyTarget={replyTarget}
            replyText={replyText}
            onReplyTextChange={setReplyText}
            onReplyTargetChange={handleReplyTarget}
            onSubmitReply={handleSubmitReply}
            onLike={handleCommentLike}
            onDelete={handleCommentDelete}
            submitting={submittingComment}
          />

          <ConfirmDeleteModal
            visible={deleteDialog.visible}
            message={deleteDialog.message}
            onClose={closeDeleteDialog}
            onConfirm={handleConfirmDelete}
            loading={deleteLoading}
          />
        </div>
      </div>

      <div className="mt-4 text-center">
        <Link to="/community" className="btn btn-outline-secondary">
          <i className="fas fa-arrow-left me-1" />返回社区
        </Link>
      </div>
    </div>
  );
};

export default CommunityPostDetail;
