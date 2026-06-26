/**
 * @file UserPublicProfile.js
 * @module PawRescue
 * @description 页面组件：UserPublicProfile。
 */

import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { adminAPI, authAPI, usersAPI } from '../api/api';
import { POST_CATEGORIES } from '../constants/site';
import { isAdminUser } from '../components/AdminRoute';
const formatDate = (value) => {
  if (!value) return '-';
  return new Date(value).toLocaleString();
};
const PostList = ({ posts, emptyText }) => {
  if (!posts?.length) {
    return <p className="text-muted">{emptyText}</p>;
  }
  return (
    <ul className="list-group mb-4">
      {posts.map((p) => (
        <li key={p.id} className="list-group-item">
          <Link to={`/community/${p.id}`} className="fw-semibold text-decoration-none">
            {p.title}
          </Link>
          <div className="small text-muted mt-1">
            <span className="badge bg-secondary me-2">
              {POST_CATEGORIES[p.category] || p.category}
            </span>
            发布于 {formatDate(p.created_at)}
          </div>
        </li>
      ))}
    </ul>
  );
};
const UserPublicProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);
  const [tab, setTab] = useState('all');
  const [blockLoading, setBlockLoading] = useState(false);
  useEffect(() => {
    (async () => {
      try {
        const [pubRes, meRes] = await Promise.all([
          usersAPI.getPublicProfile(id),
          localStorage.getItem('token') ? authAPI.getProfile().catch(() => null) : null,
        ]);
        setErrorMsg('');
        setData(pubRes.data);
        if (meRes) setCurrentUser(meRes.data);
      } catch (err) {
        console.error(err);
        setData(null);
        const detail = err.response?.data?.detail;
        if (err.response?.status === 403 && detail === 'blocked_by_user') {
          setErrorMsg('对方已将你拉黑，无法查看其主页');
        } else {
          setErrorMsg('用户不存在或无法查看');
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);
  const isSelf = currentUser && String(currentUser.id) === String(id);
  const handleBan = async () => {
    if (!window.confirm('确定封禁该用户？')) return;
    try {
      await adminAPI.updateUser(id, { status: 1 });
      alert('已封禁');
      navigate('/admin?tab=users');
    } catch (err) {
      alert('操作失败');
    }
  };
  const handleBlock = async () => {
    if (!data) return;
    const blockedByMe = !!data.is_blocked_by_me;
    const confirmed = blockedByMe
      ? window.confirm('确定取消拉黑该用户？')
      : window.confirm('确定拉黑该用户？对方将无法查看你的主页、帖子，也无法评论。');
    if (!confirmed) return;
    setBlockLoading(true);
    try {
      if (blockedByMe) {
        await usersAPI.unblockUser(id);
        setData((prev) => (prev ? { ...prev, is_blocked_by_me: false } : prev));
        alert('已取消拉黑');
      } else {
        await usersAPI.blockUser(id);
        setData((prev) => (prev ? { ...prev, is_blocked_by_me: true } : prev));
        alert('已拉黑');
      }
    } catch (err) {
      alert('操作失败');
    } finally {
      setBlockLoading(false);
    }
  };
  if (loading) {
    return <div className="text-center py-5"><div className="spinner-border text-success" /></div>;
  }
  if (!data) {
    return <div className="alert alert-danger">{errorMsg || '用户不存在或已禁用'}</div>;
  }
  const showAdminActions = currentUser && isAdminUser(currentUser);
  const isBanned = data?.is_banned;
  return (
    <div className="py-3">
      {isBanned && (
        <div className="alert alert-warning">
          {'\u8be5\u7528\u6237\u5df2\u88ab\u5c01\u7981\uff0c\u4e3b\u9875\u5185\u5bb9\u4e0d\u53ef\u89c1\u3002'}
        </div>
      )}
      <div className="card shadow-sm mb-4">
        <div className="card-body d-flex gap-3 align-items-center flex-wrap">
          {data.avatar_url ? (
            <img src={data.avatar_url} alt="" className="rounded-circle" style={{ width: 72, height: 72, objectFit: 'cover' }} />
          ) : (
            <div className="bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center" style={{ width: 72, height: 72 }}>
              <i className="fas fa-user fa-2x" />
            </div>
          )}
          <div>
            <h2 className="h4 mb-1">{data.nickname || data.username}</h2>
            <p className="text-muted mb-0 small">@{data.username}</p>
            {data.is_blocked_by_me && (
              <span className="badge bg-danger-subtle text-danger border mt-1">已拉黑</span>
            )}
          </div>
          <div className="ms-auto d-flex gap-2 flex-wrap">
            {isSelf && (
              <Link to="/community/publish" className="btn btn-success btn-sm">发帖</Link>
            )}
            {currentUser && !isSelf && (
              <button
                type="button"
                className="btn btn-outline-danger btn-sm"
                disabled={blockLoading}
                onClick={handleBlock}
              >
                {data.is_blocked_by_me ? '取消拉黑' : '拉黑用户'}
              </button>
            )}
            {showAdminActions && (
              <>
                <Link to="/admin?tab=users" className="btn btn-outline-primary btn-sm">后台用户管理</Link>
                <button type="button" className="btn btn-outline-danger btn-sm" onClick={handleBan}>封禁用户</button>
              </>
            )}
          </div>
        </div>
      </div>
      <h5 className="mb-3">{isSelf ? '我发布的帖子' : 'TA 发布的帖子'}</h5>
      {!isBanned && (
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button type="button" className={`nav-link ${tab === 'all' ? 'active' : ''}`} onClick={() => setTab('all')}>
            全部
          </button>
        </li>
        <li className="nav-item">
          <button type="button" className={`nav-link ${tab === 'pet' ? 'active' : ''}`} onClick={() => setTab('pet')}>
            养宠经验
          </button>
        </li>
        <li className="nav-item">
          <button type="button" className={`nav-link ${tab === 'lost' ? 'active' : ''}`} onClick={() => setTab('lost')}>
            报失寻主
          </button>
        </li>
      </ul>
      )}
      {!isBanned && tab === 'all' && (
        <PostList posts={data.community_posts} emptyText="暂无发布的社区帖子" />
      )}
      {!isBanned && tab === 'pet' && (
        <PostList
          posts={data.pet_experience_posts || data.community_posts?.filter((p) => p.category === 'pet_experience')}
          emptyText="暂无养宠经验帖"
        />
      )}
      {!isBanned && tab === 'lost' && (
        data.lost_found_posts?.length ? (
          <ul className="list-group">
            {data.lost_found_posts.map((p) => (
              <li key={p.id} className="list-group-item">
                <Link to={`/lost-found/${p.id}`}>{p.pet_species}</Link>
                <span className="small text-muted ms-2">发布于 {formatDate(p.created_at)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-muted">暂无报失信息</p>
        )
      )}
    </div>
  );
};

export default UserPublicProfile;

