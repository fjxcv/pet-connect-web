/**
 * @file CmsDetail.js
 * @module PawRescue
 * @description 页面组件：CmsDetail。
 */

import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cmsAPI } from '../api/api';
import { ARTICLE_TYPES } from '../constants/site';
const CmsDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const fetchedRef = useRef(false);
  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    const fetchArticle = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await cmsAPI.getArticle(id);
        setArticle(response.data);
      } catch (err) {
        setError('文章不存在或加载失败。');
        console.error('Error fetching article:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [id]);
  const requireAuth = () => {
    if (!localStorage.getItem('token')) {
      alert('请先登录');
      navigate('/login');
      return false;
    }
    return true;
  };
  const handleFavorite = async () => {
    if (!requireAuth()) return;
    setActionLoading(true);
    try {
      if (article.is_favorited) {
        await cmsAPI.unfavoriteArticle(id);
        setArticle((a) => ({ ...a, is_favorited: false }));
      } else {
        await cmsAPI.favoriteArticle(id);
        setArticle((a) => ({ ...a, is_favorited: true }));
      }
    } catch (err) {
      console.error(err);
      alert('收藏操作失败，请重试。');
    } finally {
      setActionLoading(false);
    }
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
  if (error || !article) {
    return (
      <div className="text-center">
        <div className="alert alert-danger">{error || '文章未找到'}</div>
        <Link to="/cms" className="btn btn-outline-secondary">返回列表</Link>
      </div>
    );
  }
  const offlineNotice =
    article.status === 2
      ? '此文章已下线，仅管理员可见'
      : article.status === 0
        ? '此文章为草稿，仅管理员可见'
        : null;
  return (
    <div className="py-3">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/">首页</Link></li>
          <li className="breadcrumb-item"><Link to="/cms">资讯中心</Link></li>
          <li className="breadcrumb-item active">{article.title}</li>
        </ol>
      </nav>
      {offlineNotice && (
        <div className="alert alert-warning d-flex align-items-center" role="alert">
          <i className="fas fa-eye-slash me-2"></i>
          <span>{offlineNotice}</span>
        </div>
      )}
      <article className="card shadow-sm">
        {article.cover_url && (
          <img src={article.cover_url} className="card-img-top" alt={article.title} style={{ maxHeight: '400px', objectFit: 'cover' }} />
        )}
        <div className="card-body">
          <div className="mb-3">
            <span className="badge bg-success me-2">
              {ARTICLE_TYPES[article.article_type] || article.article_type}
            </span>
            {article.is_pinned && <span className="badge bg-warning text-dark">置顶</span>}
          </div>
          <h1 className="card-title mb-3">{article.title}</h1>
          <div className="text-muted small mb-4">
            {article.author && <span className="me-3"><i className="fas fa-user me-1"></i>{article.author.username}</span>}
            <span className="me-3"><i className="fas fa-eye me-1"></i>{article.view_count || 0} 次阅读</span>
            {article.published_at && (
              <span><i className="fas fa-calendar me-1"></i>{new Date(article.published_at).toLocaleDateString()}</span>
            )}
          </div>
          {article.summary && <p className="lead text-muted">{article.summary}</p>}
          <div className="article-content markdown-preview" style={{ lineHeight: 1.8 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{article.content || ''}</ReactMarkdown>
          </div>
        </div>
      </article>
      <div className="mt-4 d-flex flex-wrap justify-content-center gap-2">
        <button
          type="button"
          className={`btn ${article.is_favorited ? 'btn-warning' : 'btn-outline-warning'}`}
          onClick={handleFavorite}
          disabled={actionLoading}
        >
          <i className="fas fa-star me-1"></i>
          {article.is_favorited ? '已收藏' : '收藏'}
        </button>
        <Link to="/cms" className="btn btn-outline-secondary">
          <i className="fas fa-arrow-left me-1"></i>返回列表
        </Link>
      </div>
    </div>
  );
};

export default CmsDetail;

