import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI, cmsAPI, communityAPI } from '../api/api';
import { ARTICLE_TYPES, POST_CATEGORIES } from '../constants/site';
import { confirmLogout } from '../utils/auth';
import { isAdminUser } from '../components/AdminRoute';
import { useManageMode } from '../context/ManageModeContext';

const ROLE_LABELS = {
  admin: { label: '管理员', badge: 'bg-danger' },
  user: { label: '普通用户', badge: 'bg-success' },
  visitor: { label: '访客', badge: 'bg-secondary' },
};

const formatDate = (value) => {
  if (!value) return '-';
  return new Date(value).toLocaleString();
};

const AccountCenter = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mainTab, setMainTab] = useState('posts');
  const [favTab, setFavTab] = useState('community');
  const [myPosts, setMyPosts] = useState([]);
  const [postsLoading, setPostsLoading] = useState(false);
  const [postFavorites, setPostFavorites] = useState([]);
  const [articleFavorites, setArticleFavorites] = useState([]);
  const [favLoading, setFavLoading] = useState(false);
  const [actionId, setActionId] = useState(null);

  const profile = user?.profile || {};
  const roleInfo = ROLE_LABELS[profile.role] || ROLE_LABELS.user;
  const isAdmin = isAdminUser(user);
  const { manageMode, setManageMode } = useManageMode();

  const loadProfile = useCallback(async () => {
    const res = await authAPI.getProfile();
    setUser(res.data);
    return res.data;
  }, []);

  const loadMyPosts = useCallback(async (userId) => {
    if (!userId) return;
    setPostsLoading(true);
    try {
      const res = await communityAPI.getPosts({ author: userId });
      const list = Array.isArray(res.data) ? res.data : res.data?.results ?? [];
      setMyPosts(list);
    } catch (err) {
      console.error(err);
    } finally {
      setPostsLoading(false);
    }
  }, []);

  const loadFavorites = useCallback(async () => {
    setFavLoading(true);
    try {
      const [postsRes, articlesRes] = await Promise.all([
        communityAPI.getFavorites(),
        cmsAPI.getFavorites(),
      ]);
      setPostFavorites(postsRes.data || []);
      setArticleFavorites(articlesRes.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setFavLoading(false);
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const profileData = await loadProfile();
        await Promise.all([loadMyPosts(profileData?.id), loadFavorites()]);
      } catch (err) {
        console.error(err);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    })();
  }, [loadProfile, loadFavorites, navigate]);

  const handleUnfavoritePost = async (postId) => {
    setActionId(`post-${postId}`);
    try {
      await communityAPI.unfavoritePost(postId);
      setPostFavorites((items) => items.filter((item) => item.post?.id !== postId));
    } catch (err) {
      console.error(err);
      alert('取消收藏失败，请重试。');
    } finally {
      setActionId(null);
    }
  };

  const handleUnfavoriteArticle = async (articleId) => {
    setActionId(`article-${articleId}`);
    try {
      await cmsAPI.unfavoriteArticle(articleId);
      setArticleFavorites((items) => items.filter((item) => item.article?.id !== articleId));
    } catch (err) {
      console.error(err);
      alert('取消收藏失败，请重试。');
    } finally {
      setActionId(null);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status"></div>
        <p className="mt-2">加载个人中心...</p>
      </div>
    );
  }

  return (
    <div className="container py-4">
      <div className="card shadow-sm mb-4">
        <div className="card-body text-center py-4">
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt="头像"
              className="rounded-circle mb-3"
              style={{ width: 96, height: 96, objectFit: 'cover' }}
            />
          ) : (
            <div
              className="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
              style={{ width: 96, height: 96 }}
            >
              <i className="fas fa-user fa-3x"></i>
            </div>
          )}
          <h2 className="h4 mb-1">{profile.nickname || user?.username}</h2>
          <p className="text-muted mb-2 small">@{user?.username}</p>
          <span className={`badge ${roleInfo.badge} mb-3`}>{roleInfo.label}</span>
          <div className="d-flex flex-wrap justify-content-center gap-2">
            <Link to="/profile" className="btn btn-outline-primary btn-sm">
              <i className="fas fa-user-edit me-1"></i>编辑资料
            </Link>
            {user?.id && (
              <Link to={`/users/${user.id}`} className="btn btn-outline-secondary btn-sm">
                <i className="fas fa-id-card me-1"></i>我的主页
              </Link>
            )}
          </div>
        </div>
      </div>

      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button
            type="button"
            className={`nav-link ${mainTab === 'posts' ? 'active' : ''}`}
            onClick={() => setMainTab('posts')}
          >
            我的发布
          </button>
        </li>
        <li className="nav-item">
          <button
            type="button"
            className={`nav-link ${mainTab === 'favorites' ? 'active' : ''}`}
            onClick={() => setMainTab('favorites')}
          >
            我的收藏
          </button>
        </li>
        <li className="nav-item">
          <button
            type="button"
            className={`nav-link ${mainTab === 'business' ? 'active' : ''}`}
            onClick={() => setMainTab('business')}
          >
            我的业务
          </button>
        </li>
        <li className="nav-item">
          <button
            type="button"
            className={`nav-link ${mainTab === 'security' ? 'active' : ''}`}
            onClick={() => setMainTab('security')}
          >
            账号与安全
          </button>
        </li>
      </ul>

      {mainTab === 'posts' && (
        <div>
          <div className="d-flex justify-content-end mb-3">
            <Link to="/community/publish" className="btn btn-success btn-sm">发帖</Link>
          </div>
          {postsLoading ? (
            <div className="text-center py-4">
              <div className="spinner-border spinner-border-sm text-success" />
            </div>
          ) : myPosts.length === 0 ? (
            <p className="text-muted">
              暂无发布的帖子。
              <Link to="/community/publish" className="ms-1">去发帖</Link>
            </p>
          ) : (
            <div className="list-group">
              {myPosts.map((post) => (
                <div key={post.id} className="list-group-item text-start">
                  <div className="d-flex justify-content-between align-items-start gap-2">
                    <div className="flex-grow-1 text-start min-w-0">
                      <Link to={`/community/${post.id}`} className="fw-semibold text-decoration-none d-block text-start">
                        {post.title}
                      </Link>
                      <div className="small text-muted mt-1">
                        <span className="badge bg-secondary me-2">
                          {POST_CATEGORIES[post.category] || post.category}
                        </span>
                        发布于 {formatDate(post.created_at)}
                        {post.edited_at && (
                          <span className="ms-2">· 编辑于 {formatDate(post.edited_at)}</span>
                        )}
                      </div>
                    </div>
                    <Link to={`/community/${post.id}/edit`} className="btn btn-sm btn-outline-primary">
                      编辑
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {mainTab === 'favorites' && (
        <div>
          <ul className="nav nav-pills mb-3">
            <li className="nav-item">
              <button
                type="button"
                className={`nav-link ${favTab === 'community' ? 'active' : ''}`}
                onClick={() => setFavTab('community')}
              >
                社区帖子
              </button>
            </li>
            <li className="nav-item">
              <button
                type="button"
                className={`nav-link ${favTab === 'cms' ? 'active' : ''}`}
                onClick={() => setFavTab('cms')}
              >
                资讯收藏
              </button>
            </li>
          </ul>

          {favLoading ? (
            <div className="text-center py-4">
              <div className="spinner-border spinner-border-sm text-success"></div>
            </div>
          ) : favTab === 'community' ? (
            postFavorites.length === 0 ? (
              <p className="text-muted">
                暂无收藏的社区帖子。
                <Link to="/community" className="ms-1">去社区逛逛</Link>
              </p>
            ) : (
              <div className="list-group">
                {postFavorites.map((item) => {
                  const post = item.post;
                  if (!post) return null;
                  return (
                    <div key={item.id} className="list-group-item text-start">
                      <div className="d-flex justify-content-between align-items-start gap-2">
                        <div className="flex-grow-1 text-start min-w-0">
                          <Link to={`/community/${post.id}`} className="fw-semibold text-decoration-none d-block text-start">
                            {post.title}
                          </Link>
                          <div className="small text-muted mt-1">
                            <span className="badge bg-secondary me-2">
                              {POST_CATEGORIES[post.category] || post.category}
                            </span>
                            收藏于 {formatDate(item.created_at)}
                          </div>
                          <p className="small mb-0 mt-2 text-muted">{post.content?.slice(0, 80)}</p>
                        </div>
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-warning"
                          disabled={actionId === `post-${post.id}`}
                          onClick={() => handleUnfavoritePost(post.id)}
                        >
                          取消收藏
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )
          ) : articleFavorites.length === 0 ? (
            <p className="text-muted">
              暂无收藏的资讯。
              <Link to="/cms" className="ms-1">去资讯中心看看</Link>
            </p>
          ) : (
            <div className="list-group">
              {articleFavorites.map((item) => {
                const article = item.article;
                if (!article) return null;
                return (
                  <div key={item.id} className="list-group-item">
                    <div className="d-flex justify-content-between align-items-start gap-2">
                      <div>
                        <Link to={`/cms/${article.id}`} className="fw-semibold text-decoration-none">
                          {article.title}
                        </Link>
                        <div className="small text-muted mt-1">
                          <span className="badge bg-success me-2">
                            {ARTICLE_TYPES[article.article_type] || article.article_type}
                          </span>
                          收藏于 {formatDate(item.created_at)}
                        </div>
                        {article.summary && (
                          <p className="small mb-0 mt-2 text-muted">{article.summary}</p>
                        )}
                      </div>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-warning"
                        disabled={actionId === `article-${article.id}`}
                        onClick={() => handleUnfavoriteArticle(article.id)}
                      >
                        取消收藏
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {mainTab === 'business' && (
        <div className="row g-3">
          {isAdmin && (
            <>
              <div className="col-md-4">
                <div className="card h-100 shadow-sm border-danger">
                  <div className="card-body">
                    <h5 className="card-title"><i className="fas fa-cog me-2 text-danger"></i>管理后台</h5>
                    <p className="card-text text-muted small">用户、领养审核、宠物与资讯运营。</p>
                    <Link to="/admin" className="btn btn-danger btn-sm">进入后台</Link>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card h-100 shadow-sm">
                  <div className="card-body">
                    <h5 className="card-title"><i className="fas fa-shield-alt me-2 text-warning"></i>管理模式</h5>
                    <p className="card-text text-muted small">开启后可在前台页面快速隐藏、删除内容或封禁用户。</p>
                    <button type="button" className={`btn btn-sm ${manageMode ? 'btn-warning' : 'btn-outline-warning'}`} onClick={() => setManageMode(!manageMode)}>
                      {manageMode ? '已开启' : '开启管理模式'}
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
          <div className="col-md-4">
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                <h5 className="card-title"><i className="fas fa-hand-holding-heart me-2 text-success"></i>我的救助</h5>
                <p className="card-text text-muted small">查看我上报的救助案例。</p>
                <Link to="/my-rescues" className="btn btn-outline-success btn-sm">进入</Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {mainTab === 'security' && (
        <div className="card shadow-sm">
          <div className="card-body text-center py-4">
            <h5 className="mb-4">账号与安全</h5>
            <div className="d-grid gap-2 mx-auto w-100" style={{ maxWidth: 320 }}>
              <Link to="/profile" className="btn btn-outline-primary">
                <i className="fas fa-user-edit me-2"></i>编辑资料
              </Link>
              <Link to="/forgot-password" className="btn btn-outline-secondary">
                <i className="fas fa-key me-2"></i>修改密码
              </Link>
              <p className="small text-muted mb-0 mt-1">
                通过注册邮箱接收验证码后重置密码。
              </p>
              <button
                type="button"
                className="btn btn-outline-danger mt-2"
                onClick={() => confirmLogout(navigate)}
              >
                <i className="fas fa-sign-out-alt me-2"></i>退出登录
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountCenter;
