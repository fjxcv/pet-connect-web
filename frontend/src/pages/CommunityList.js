import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { adminAPI, communityAPI } from '../api/api';
import AdminManageBar from '../components/AdminManageBar';
import { POST_CATEGORIES } from '../constants/site';
import { useAuthPrompt } from '../context/AuthPromptContext';

const CATEGORY_TABS = [
  { key: '', label: '全部' },
  ...Object.entries(POST_CATEGORIES).map(([key, label]) => ({ key, label })),
];

const FAVORITES_TAB = { key: 'favorites', label: '我的收藏' }; // 新增收藏标签

const ORDER_OPTIONS = [
  { key: 'latest', label: '最新发布' },
  { key: 'likes', label: '最多点赞' },
];

const PAGE_SIZE = 10;

const CommunityList = () => {
  useNavigate();
  const [posts, setPosts] = useState([]);
  const [favoriteItems, setFavoriteItems] = useState([]);
  const [category, setCategory] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [searchQ, setSearchQ] = useState('');
  const [ordering, setOrdering] = useState('latest');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [likingId, setLikingId] = useState(null);
  const [favoriteMode, setFavoriteMode] = useState(false);
  const [favoritesLoading, setFavoritesLoading] = useState(false);
  const [page, setPage] = useState(1);

  const authPrompt = useAuthPrompt();

  useEffect(() => {
    const timer = setTimeout(() => setSearchQ(searchInput.trim()), 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { ordering, page };
      if (category) params.category = category;
      if (searchQ) params.q = searchQ;
      const response = await communityAPI.getPosts(params);
      const data = response.data;
      if (Array.isArray(data)) {
        setPosts(data);
      } else {
        setPosts(data?.results ?? []);
      }
    } catch (err) {
      setError('加载帖子失败，请稍后重试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [category, ordering, page, searchQ]);

  const fetchFavorites = useCallback(async () => {
    try {
      setFavoritesLoading(true);
      setError(null);
      const response = await communityAPI.getFavorites();
      const data = response.data;
      const favorites = Array.isArray(data) ? data : data?.results ?? [];
      setFavoriteItems(favorites);
    } catch (err) {
      setError('加载收藏失败，请稍后重试。');
      console.error(err);
    } finally {
      setFavoritesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (favoriteMode) {
      fetchFavorites();
      return;
    }
    fetchPosts();
  }, [fetchPosts, fetchFavorites, favoriteMode]);

  useEffect(() => {
    setPage(1);
  }, [searchQ, ordering, favoriteMode]);

  const handleCategoryTab = async (tabKey) => {
    if (tabKey === FAVORITES_TAB.key) {
      if (!authPrompt.requireAuth()) return;
      setFavoriteMode(true); // 新增：进入收藏模式
      return;
    }

    if (favoriteMode) {
      setFavoriteMode(false); // 退出收藏模式
    }
    setCategory(tabKey);
  };

  const handleAdminDelete = async (postId) => {
    if (!window.confirm('确定删除该帖子？')) return;
    try {
      await communityAPI.deletePost(postId);
      if (favoriteMode) {
        setFavoriteItems((prev) => prev.filter((item) => item.post?.id !== postId));
      } else {
        fetchPosts();
      }
    } catch (err) {
      alert('删除失败');
    }
  };

  const handleBanUser = async (userId) => {
    if (!window.confirm('确定封禁该用户？')) return;
    try {
      await adminAPI.updateUser(userId, { status: 1 });
      alert('已封禁');
    } catch (err) {
      alert('操作失败');
    }
  };

  const handleLike = async (post) => {
    if (!authPrompt.requireAuth()) return;
    setLikingId(post.id);
    try {
      if (post.is_liked) {
        await communityAPI.unlikePost(post.id);
      } else {
        await communityAPI.likePost(post.id);
      }
      if (favoriteMode) {
        setFavoriteItems((prev) =>
          prev.map((item) =>
            item.post?.id === post.id
              ? {
                  ...item,
                  post: {
                    ...item.post,
                    is_liked: !item.post.is_liked,
                    like_count: item.post.is_liked ? Math.max(0, item.post.like_count - 1) : item.post.like_count + 1,
                  },
                }
              : item
          )
        );
      } else {
        setPosts((prev) =>
          prev.map((p) =>
            p.id === post.id
              ? {
                  ...p,
                  is_liked: !p.is_liked,
                  like_count: p.is_liked ? Math.max(0, p.like_count - 1) : p.like_count + 1,
                }
              : p
          )
        );
      }
    } catch (err) {
      console.error(err);
      alert('操作失败');
    } finally {
      setLikingId(null);
    }
  };

  const handleUnfavorite = async (postId) => {
    setLikingId(postId);
    try {
      await communityAPI.unfavoritePost(postId);
      setFavoriteItems((prev) => prev.filter((item) => item.post?.id !== postId));
    } catch (err) {
      console.error(err);
      alert('取消收藏失败，请重试。');
    } finally {
      setLikingId(null);
    }
  };

  const filteredFavoriteItems = useMemo(() => {
    if (!searchQ) return favoriteItems;
    return favoriteItems.filter((item) => {
      const post = item.post || {};
      const target = `${post.title || ''} ${post.content || ''}`.toLowerCase();
      return target.includes(searchQ.toLowerCase());
    });
  }, [favoriteItems, searchQ]);

  const sortedFavoriteItems = useMemo(() => {
    const items = [...filteredFavoriteItems];
    if (ordering === 'likes') {
      items.sort((a, b) => (b.post?.like_count || 0) - (a.post?.like_count || 0));
    } else {
      items.sort((a, b) => new Date(b.post?.created_at) - new Date(a.post?.created_at));
    }
    return items;
  }, [filteredFavoriteItems, ordering]);

  const pageCount = Math.max(1, Math.ceil(sortedFavoriteItems.length / PAGE_SIZE));
  const pagedFavoriteItems = sortedFavoriteItems.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  useEffect(() => {
    if (favoriteMode && page > pageCount) {
      setPage(pageCount);
    }
  }, [favoriteMode, page, pageCount]);

  const renderPagination = (count) => {
    if (count <= 1) return null;
    return (
      <nav aria-label="分页导航" className="mt-3">
        <ul className="pagination justify-content-center">
          <li className={`page-item ${page === 1 ? 'disabled' : ''}`}>
            <button type="button" className="page-link" onClick={() => setPage((prev) => Math.max(1, prev - 1))}>
              上一页
            </button>
          </li>
          {Array.from({ length: count }, (_, index) => (
            <li key={index + 1} className={`page-item ${page === index + 1 ? 'active' : ''}`}>
              <button type="button" className="page-link" onClick={() => setPage(index + 1)}>
                {index + 1}
              </button>
            </li>
          ))}
          <li className={`page-item ${page === count ? 'disabled' : ''}`}>
            <button type="button" className="page-link" onClick={() => setPage((prev) => Math.min(count, prev + 1))}>
              下一页
            </button>
          </li>
        </ul>
      </nav>
    );
  };

  const getTabClass = (tabKey) => {
    if (favoriteMode) {
      return tabKey === FAVORITES_TAB.key ? 'nav-link active' : 'nav-link text-muted';
    }
    return `nav-link ${category === tabKey ? 'active' : ''}`;
  };

  const currentPosts = favoriteMode ? pagedFavoriteItems.map((item) => item.post).filter(Boolean) : posts;
  const currentLoading = favoriteMode ? favoritesLoading : loading;
  const currentEmptyText = favoriteMode ? '暂无收藏的帖子' : '暂无帖子';

  return (
    <div className="py-3">
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
        <h2><i className="fas fa-comments me-2 text-success"></i>社区交流</h2>
        <Link to="/community/publish" className="btn btn-success">
          <i className="fas fa-pen me-1"></i>发帖
        </Link>
      </div>

      <div className="row g-2 mb-3">
        <div className="col-md-8">
          <div className="input-group">
            <span className="input-group-text"><i className="fas fa-search" /></span>
            <input
              type="search"
              className="form-control"
              placeholder="搜索标题或正文..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </div>
        </div>
        <div className="col-md-4">
          <select
            className="form-select"
            value={ordering}
            onChange={(e) => setOrdering(e.target.value)}
          >
            {ORDER_OPTIONS.map((opt) => (
              <option key={opt.key} value={opt.key}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <ul className="nav nav-pills mb-4 tab-wrap">
        {CATEGORY_TABS.map((tab) => (
          <li className="nav-item" key={tab.key || 'all'}>
            <button
              type="button"
              className={getTabClass(tab.key)}
              onClick={() => handleCategoryTab(tab.key)}
            >
              {tab.label}
            </button>
          </li>
        ))}
        <li className="nav-item">
          <button
            type="button"
            className={getTabClass(FAVORITES_TAB.key)}
            onClick={() => handleCategoryTab(FAVORITES_TAB.key)}
          >
            {FAVORITES_TAB.label} {/* 新增收藏标签 */}
          </button>
        </li>
      </ul>

      {currentLoading && (
        <div className="text-center py-5">
          <div className="spinner-border text-success" role="status">
            <span className="visually-hidden">加载中...</span>
          </div>
        </div>
      )}

      {error && <div className="alert alert-danger">{error}</div>}

      {!currentLoading && !error && (
        <div className="list-group">
          {currentPosts.length === 0 ? (
            <div className="text-center text-muted py-5">{currentEmptyText}</div>
          ) : (
            currentPosts.map((post) => (
              <div key={post.id} className="list-group-item list-group-item-action mb-2 rounded shadow-sm">
                <AdminManageBar
                  userId={post.author?.id}
                  onHide={() => handleAdminDelete(post.id)}
                  onDelete={() => handleAdminDelete(post.id)}
                  onBanUser={() => handleBanUser(post.author.id)}
                />
                <div className="d-flex w-100 justify-content-between align-items-start">
                  <div className="flex-grow-1 text-start">
                    <div className="mb-1">
                      <span className="badge bg-success me-2">
                        {POST_CATEGORIES[post.category] || post.category}
                      </span>
                      {post.author && (
                        <Link to={`/users/${post.author.id}`} className="text-muted small">{post.author.username}</Link>
                      )}
                    </div>
                    <Link to={`/community/${post.id}`} className="text-decoration-none text-dark d-block text-start">
                      <h5 className="mb-1">{post.title}</h5>
                    </Link>
                    <p className="mb-2 text-muted small text-start">{post.content?.slice(0, 120)}</p>
                    <small className="text-muted">
                      {new Date(post.created_at).toLocaleString()} · {post.comment_count} 评论
                    </small>
                  </div>
                  <button
                    type="button"
                    className={`btn btn-sm ms-3 flex-shrink-0 ${favoriteMode ? 'btn-warning' : post.is_liked ? 'btn-danger' : 'btn-outline-danger'}`}
                    onClick={() => (favoriteMode ? handleUnfavorite(post.id) : handleLike(post))}
                    disabled={likingId === post.id}
                  >
                    <i className="fas fa-heart me-1"></i>
                    {favoriteMode ? '已收藏' : post.like_count}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {favoriteMode && renderPagination(pageCount)}

      
    </div>
  );
};

export default CommunityList;
