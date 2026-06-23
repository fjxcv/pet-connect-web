import React, { useState } from 'react';
import './CommentThread.css';

const REPLY_PREVIEW = 3;

const displayName = (author) => author?.profile?.nickname || author?.username || '用户';

const CommentRow = ({
  comment,
  postAuthorId,
  currentUserId,
  isAdminViewer,
  onLike,
  onDelete,
  onReply,
  isReply = false,
}) => {
  const canDelete = currentUserId && (
    comment.author?.id === currentUserId
    || postAuthorId === currentUserId
    || isAdminViewer
  );

  return (
    <div className={isReply ? 'comment-reply-item' : ''}>
      <div className={isReply ? 'comment-reply-header' : 'comment-header'}>
        <span className="comment-author">{displayName(comment.author)}</span>
        {comment.is_post_author && (
          <span className="badge bg-success badge-op">楼主</span>
        )}
        {comment.is_admin && (
          <span className="badge bg-danger badge-op">管理员</span>
        )}
        {comment.reply_to && (
          <span className="comment-reply-to">回复 @{comment.reply_to}</span>
        )}
        <span className="comment-meta">{new Date(comment.created_at).toLocaleString()}</span>
        <div className="comment-actions">
          <button
            type="button"
            className={`comment-action-btn${comment.is_liked ? ' active' : ''}`}
            onClick={() => onLike(comment)}
            title={currentUserId ? '点赞' : '登录后点赞'}
          >
            <span>❤</span>
            <span className="comment-action-count">{comment.like_count || 0}</span>
          </button>
          {currentUserId && (
            <button type="button" className="comment-action-btn" onClick={() => onReply(comment)}>
              回复
            </button>
          )}
          {canDelete && (
            <button type="button" className="comment-action-btn comment-action-danger" onClick={() => onDelete(comment)}>
              删除
            </button>
          )}
        </div>
      </div>
      <p className="comment-content">{comment.content}</p>
    </div>
  );
};

const ReplyForm = ({
  replyTarget,
  replyText,
  onReplyTextChange,
  onSubmitReply,
  onCancel,
  submitting,
}) => (
  <div className="comment-reply-form">
    <div className="small text-muted mb-1">
      回复 {displayName(replyTarget.author)}
    </div>
    <textarea
      className="form-control form-control-sm mb-2"
      rows={2}
      value={replyText}
      onChange={(e) => onReplyTextChange(e.target.value)}
      placeholder="写下回复..."
    />
    <div className="d-flex gap-2">
      <button
        type="button"
        className="btn btn-success btn-sm"
        disabled={submitting || !replyText.trim()}
        onClick={onSubmitReply}
      >
        {submitting ? '提交中...' : '发送回复'}
      </button>
      <button type="button" className="btn btn-outline-secondary btn-sm" onClick={onCancel}>
        取消
      </button>
    </div>
  </div>
);

const ReplyList = ({
  replies,
  postAuthorId,
  currentUserId,
  isAdminViewer,
  onLike,
  onDelete,
  onReply,
  replyTarget,
  replyText,
  onReplyTextChange,
  onSubmitReply,
  onCancelReply,
  submitting,
}) => {
  const [expanded, setExpanded] = useState(false);
  if (!replies?.length) return null;

  const hiddenCount = Math.max(0, replies.length - REPLY_PREVIEW);
  const visible = expanded || hiddenCount === 0 ? replies : replies.slice(0, REPLY_PREVIEW);

  return (
    <div className="comment-replies">
      {visible.map((reply) => (
        <div key={reply.id}>
          <CommentRow
            comment={reply}
            postAuthorId={postAuthorId}
            currentUserId={currentUserId}
            isAdminViewer={isAdminViewer}
            onLike={onLike}
            onDelete={onDelete}
            onReply={onReply}
            isReply
          />
          {replyTarget?.id === reply.id && (
            <ReplyForm
              replyTarget={replyTarget}
              replyText={replyText}
              onReplyTextChange={onReplyTextChange}
              onSubmitReply={onSubmitReply}
              onCancel={onCancelReply}
              submitting={submitting}
            />
          )}
        </div>
      ))}
      {hiddenCount > 0 && !expanded && (
        <button type="button" className="comment-expand-btn" onClick={() => setExpanded(true)}>
          展开 {hiddenCount} 条回复
        </button>
      )}
      {expanded && hiddenCount > 0 && (
        <button type="button" className="comment-expand-btn" onClick={() => setExpanded(false)}>
          收起回复
        </button>
      )}
    </div>
  );
};

const CommentFloor = ({
  comment,
  postAuthorId,
  currentUserId,
  isAdminViewer,
  onLike,
  onDelete,
  onReply,
  replyTarget,
  replyText,
  onReplyTextChange,
  onSubmitReply,
  onCancelReply,
  submitting,
}) => (
  <div className="comment-floor">
    <div className="comment-floor-no">#{comment.floor}</div>
    <div className="comment-floor-body">
      <CommentRow
        comment={comment}
        postAuthorId={postAuthorId}
        currentUserId={currentUserId}
        isAdminViewer={isAdminViewer}
        onLike={onLike}
        onDelete={onDelete}
        onReply={onReply}
      />
      {replyTarget?.id === comment.id && (
        <ReplyForm
          replyTarget={replyTarget}
          replyText={replyText}
          onReplyTextChange={onReplyTextChange}
          onSubmitReply={onSubmitReply}
          onCancel={onCancelReply}
          submitting={submitting}
        />
      )}
      <ReplyList
        replies={comment.replies}
        postAuthorId={postAuthorId}
        currentUserId={currentUserId}
        isAdminViewer={isAdminViewer}
        onLike={onLike}
        onDelete={onDelete}
        onReply={onReply}
        replyTarget={replyTarget}
        replyText={replyText}
        onReplyTextChange={onReplyTextChange}
        onSubmitReply={onSubmitReply}
        onCancelReply={onCancelReply}
        submitting={submitting}
      />
    </div>
  </div>
);

const CommentThread = ({
  comments,
  post,
  currentUser,
  replyTarget,
  replyText,
  onReplyTextChange,
  onReplyTargetChange,
  onSubmitReply,
  onLike,
  onDelete,
  submitting,
}) => {
  const postAuthorId = post?.author?.id;
  const currentUserId = currentUser?.id;
  const isAdminViewer = currentUser?.profile?.role === 'admin';

  if (!comments?.length) {
    return <p className="text-muted">暂无评论</p>;
  }

  return (
    <div className="comment-thread">
      {comments.map((comment) => (
        <CommentFloor
          key={comment.id}
          comment={comment}
          postAuthorId={postAuthorId}
          currentUserId={currentUserId}
          isAdminViewer={isAdminViewer}
          onLike={onLike}
          onDelete={onDelete}
          onReply={onReplyTargetChange}
          replyTarget={replyTarget}
          replyText={replyText}
          onReplyTextChange={onReplyTextChange}
          onSubmitReply={onSubmitReply}
          onCancelReply={() => {
            onReplyTargetChange(null);
            onReplyTextChange('');
          }}
          submitting={submitting}
        />
      ))}
    </div>
  );
};

export default CommentThread;
