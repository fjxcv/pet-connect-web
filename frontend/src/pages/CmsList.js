/**
 * @file CmsList.js
 * @module PawRescue
 * @description 页面组件：CmsList。
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { cmsAPI } from '../api/api';
import AdminManageBar from '../components/AdminManageBar';
import { ARTICLE_TYPES } from '../constants/site';
const TYPE_TABS = [
  { key: '', label: '全部' },
  ...Object.entries(ARTICLE_TYPES)
    .filter(([key]) => key !== 'law')
    .map(([key, label]) => ({ key, label })),
];
// 文章状态：0=草稿，1=已发布，2=已下线（仅管理员能在前台看到非已发布文章）
const STATUS_BADGES = {
  0: { label: '草稿', className: 'bg-secondary' },
  2: { label: '已下线', className: 'bg-danger' },
};
const CmsList = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [articles, setArticles] = useState([]);
  const [activeType, setActiveType] = useState(searchParams.get('type') || '');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const debounceRef = useRef(null);
  // 加载文章列表
  const fetchArticles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (activeType) params.type = activeType;
      if (searchKeyword) params.search = searchKeyword;
      const response = await cmsAPI.getArticles(params);
      setArticles(Array.isArray(response.data) ? response.data : response.data?.results ?? []);
    } catch (err) {
      setError('加载文章失败，请稍后重试。');
      console.error('Error fetching articles:', err);
    } finally {
      setLoading(false);
    }
  }, [activeType, searchKeyword]);
  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);
  // 就地更新某篇文章的状态，便于下线/上线后立即反映在卡片上
  const patchArticleStatus = async (id, status) => {
    await cmsAPI.updateArticle(id, { status });
    setArticles((list) => list.map((a) => (a.id === id ? { ...a, status } : a)));
  };
  // 实时搜索：输入变化后延迟 300ms 自动搜索
  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchInput(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchKeyword(value.trim());
    }, 300);
  };
  // 搜索提交（点击按钮时立即搜索）
  const handleSearch = (e) => {
    e.preventDefault();
    if (debounceRef.current) clearTimeout(debounceRef.current);
    setSearchKeyword(searchInput.trim());
  };
  // 切换类型时重置搜索
  const handleTypeChange = (type) => {
    setActiveType(type);
    setSearchKeyword('');
    setSearchInput('');
  };
  // 组件卸载时清除定时器
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);
  return (
    <div className="py-3">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2><i className="fas fa-newspaper me-2 text-success"></i>资讯中心</h2>
      </div>
      {/* 类型标签 */}
      <ul className="nav nav-pills mb-3 flex-wrap gap-1">
        {TYPE_TABS.map((tab) => (
          <li className="nav-item" key={tab.key || 'all'}>
            <button
              type="button"
              className={`nav-link ${activeType === tab.key ? 'active' : ''}`}
              onClick={() => handleTypeChange(tab.key)}
            >
              {tab.label}
            </button>
          </li>
        ))}
      </ul>
      {/* 搜索框 */}
      <div className="mb-4">
        <form onSubmit={handleSearch}>
          <div className="input-group" style={{ maxWidth: '400px' }}>
            <input
              type="text"
              className="form-control"
              placeholder="搜索文章关键词..."
              value={searchInput}
              onChange={handleInputChange}
            />
            <button type="submit" className="btn btn-success">
              <i className="fas fa-search me-1"></i>搜索
            </button>
          </div>
        </form>
      </div>
      {/* 文章列表 */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-success" role="status">
            <span className="visually-hidden">加载中...</span>
          </div>
        </div>
      )}
      {error && <div className="alert alert-danger">{error}</div>}
      {!loading && !error && (
        <div className="row">
          {articles.length === 0 ? (
            <div className="col-12 text-center text-muted py-5">
              {searchKeyword ? '未找到匹配的文章' : '暂无文章'}
            </div>
          ) : (
            articles.map((article) => {
              const statusBadge = STATUS_BADGES[article.status];
              const isOffline = !!statusBadge;
              return (
                <div key={article.id} className="col-md-6 col-lg-4 mb-4">
                  <div className={`card h-100 shadow-sm${isOffline ? ' cms-card--offline' : ''}`}>
                    {article.cover_url && (
                      <img
                        src={article.cover_url}
                        className="card-img-top"
                        alt={article.title}
                        style={{ height: '180px', objectFit: 'cover' }}
                      />
                    )}
                    <div className="card-body d-flex flex-column">
                      <AdminManageBar
                        onEdit={() => navigate('/admin?tab=cms')}
                        onHide={article.status !== 2 ? () => patchArticleStatus(article.id, 2) : undefined}
                        onPublish={article.status !== 1 ? () => patchArticleStatus(article.id, 1) : undefined}
                      />
                      <div className="mb-2 d-flex flex-wrap align-items-center gap-1">
                        <span className="badge bg-success">
                          {ARTICLE_TYPES[article.article_type] || article.article_type}
                        </span>
                        {article.is_pinned && <span className="badge bg-warning text-dark">置顶</span>}
                        {statusBadge && (
                          <span className={`badge ${statusBadge.className}`}>
                            <i className="fas fa-eye-slash me-1"></i>{statusBadge.label}
                          </span>
                        )}
                      </div>
                      <h5 className="card-title">{article.title}</h5>
                      <p className="card-text text-muted small flex-grow-1">
                        {article.summary || article.content?.slice(0, 100)}
                      </p>
                      <div className="d-flex justify-content-between align-items-center mt-2">
                        <small className="text-muted">
                          <i className="fas fa-eye me-1"></i>{article.view_count || 0}
                        </small>
                        <Link to={`/cms/${article.id}`} className="btn btn-outline-success btn-sm">
                          阅读全文
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};

export default CmsList;

