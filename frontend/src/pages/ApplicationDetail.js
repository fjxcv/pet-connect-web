/**
 * @file ApplicationDetail.js
 * @module PawRescue
 * @description 页面组件：ApplicationDetail。
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { adoptAPI } from '../api/api';
// ===== 格式化时间 =====
const formatDateTime = (dateStr) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hour = String(d.getHours()).padStart(2, '0');
  const minute = String(d.getMinutes()).padStart(2, '0');
  return `${year}.${month}.${day} ${hour}:${minute}`;
};
// ===== 判断详情类型 =====
const getDetailType = (app) => {
  // 核验失败优先（更具体的失败阶段）
  if (app.verify_status === 'failed') {
    return {
      title: '核验失败',
      subtitle: '核验失败详情',
      reason: app.verify_note || '管理员未填写原因',
      time: app.verified_at || app.updated_at,
      badge: 'danger',
    };
  }
  // 审核拒绝
  if (app.online_status === 'rejected') {
    return {
      title: '审核拒绝',
      subtitle: '驳回申请详情',
      reason: app.audit_opinion || '管理员未填写原因',
      time: app.audited_at || app.updated_at,
      badge: 'danger',
    };
  }
  return null;
};
const ApplicationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    const fetchDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await adoptAPI.getById(id);
        setApplication(res.data);
      } catch (err) {
        if (err.response?.status === 403) {
          setError('您无权查看该申请记录。');
        } else if (err.response?.status === 404) {
          setError('未找到该申请记录。');
        } else {
          setError('加载详情失败，请稍后重试。');
        }
        console.error('Error fetching application detail:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id, navigate]);
  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
        <p className="mt-2">正在加载详情...</p>
      </div>
    );
  }
  if (error || !application) {
    return (
      <div className="container py-4">
        <div className="alert alert-danger">{error || '未找到申请记录。'}</div>
        <Link to="/my-applications" className="btn btn-outline-success">
          <i className="fas fa-arrow-left me-1"></i>返回申请列表
        </Link>
      </div>
    );
  }
  const detail = getDetailType(application);
  if (!detail) {
    return (
      <div className="container py-4">
        <div className="alert alert-info">
          该申请当前状态为 {application.online_status}，无需查看驳回详情。
        </div>
        <Link to="/my-applications" className="btn btn-outline-success">
          <i className="fas fa-arrow-left me-1"></i>返回申请列表
        </Link>
      </div>
    );
  }
  return (
    <div className="application-detail-page">
      {/* ===== 面包屑导航 ===== */}
      <div className="detail-breadcrumb">
        <div className="container">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb mb-0">
              <li className="breadcrumb-item"><Link to="/">首页</Link></li>
              <li className="breadcrumb-item"><Link to="/pets">领养列表</Link></li>
              <li className="breadcrumb-item"><Link to="/my-applications">我的申请与核验</Link></li>
              <li className="breadcrumb-item active" aria-current="page">{detail.title}</li>
            </ol>
          </nav>
        </div>
      </div>
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-lg-8 col-xl-7">
            {/* ===== 宠物信息摘要 ===== */}
            <div className="pet-summary-bar mb-4">
              <img
                src={application.pet?.photo_url || 'https://via.placeholder.com/48x48?text=Pet'}
                className="pet-summary-thumb"
                alt={application.pet?.name || '宠物'}
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/48x48?text=Pet';
                }}
              />
              <div className="pet-summary-text">
                <span className="pet-summary-label">申请宠物</span>
                <span className="pet-summary-name-text">{application.pet?.name || '未知宠物'}</span>
              </div>
              <span className="pet-summary-time">
                <i className="far fa-clock me-1"></i>
                申请时间：{formatDateTime(application.created_at)}
              </span>
            </div>
            {/* ===== 详情卡片 ===== */}
            <div className="detail-card">
              {/* 标题区 */}
              <div className={`detail-card-header bg-${detail.badge}`}>
                <div className="detail-status-icon">
                  <i className="fas fa-times-circle fa-2x"></i>
                </div>
                <h2 className="detail-card-title">{detail.title}</h2>
                <p className="detail-card-time mb-0">
                  {detail.title === '核验失败' ? '核验' : '审核'}时间：{formatDateTime(detail.time)}
                </p>
              </div>
              {/* 详情区 */}
              <div className="detail-card-body">
                <h5 className="detail-section-title">
                  <i className="fas fa-file-alt me-2"></i>{detail.subtitle}
                </h5>
                <div className="reason-box">
                  <div className="reason-label">
                    <i className="fas fa-pen me-2"></i>
                    {detail.title === '核验失败' ? '核验失败' : '驳回'}原因
                  </div>
                  <div className="reason-content">
                    {detail.reason.split('\n').map((line, i) => (
                      <p key={i} className="reason-line">{line || ' '}</p>
                    ))}
                  </div>
                </div>
              </div>
              {/* 操作区 */}
              <div className="detail-card-footer">
                <Link to="/my-applications" className="btn btn-submit px-4">
                  <i className="fas fa-arrow-left me-2"></i>返回申请列表
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* ===== 样式 ===== */}
      <style>{`
        .application-detail-page {
          background-color: #FAFAFA;
          min-height: 100vh;
          padding-bottom: 3rem;
        }
        .detail-breadcrumb {
          background: white;
          border-bottom: 1px solid #eee;
          padding: 0.75rem 0;
        }
        .breadcrumb { font-size: 0.9rem; }
        /* 宠物摘要条 */
        .pet-summary-bar {
          display: flex;
          align-items: center;
          gap: 1rem;
          background: white;
          border-radius: 12px;
          padding: 1rem 1.25rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.04);
          flex-wrap: wrap;
        }
        .pet-summary-thumb {
          width: 48px;
          height: 48px;
          border-radius: 10px;
          object-fit: cover;
          border: 2px solid #eee;
          flex-shrink: 0;
        }
        .pet-summary-text {
          display: flex;
          flex-direction: column;
          flex: 1;
        }
        .pet-summary-label {
          font-size: 0.75rem;
          color: #999;
        }
        .pet-summary-name-text {
          font-size: 1.05rem;
          font-weight: 600;
          color: #333;
        }
        .pet-summary-time {
          font-size: 0.85rem;
          color: #888;
          white-space: nowrap;
        }
        /* 详情卡片 */
        .detail-card {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        /* 标题头部 */
        .detail-card-header {
          padding: 2rem 2rem 1.5rem;
          text-align: center;
          color: white;
        }
        .detail-card-header.bg-danger {
          background: linear-gradient(135deg, #dc3545, #c0392b);
        }
        .detail-status-icon {
          margin-bottom: 0.75rem;
          opacity: 0.9;
        }
        .detail-card-title {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          letter-spacing: 2px;
        }
        .detail-card-time {
          font-size: 0.9rem;
          opacity: 0.85;
        }
        /* 详情主体 */
        .detail-card-body {
          padding: 2rem;
        }
        .detail-section-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #333;
          margin-bottom: 1.25rem;
          padding-bottom: 0.75rem;
          border-bottom: 2px solid #eee;
        }
        .detail-section-title i {
          color: #dc3545;
        }
        /* 原因展示框 */
        .reason-box {
          background: #fdf5f5;
          border: 1px solid #f5c6cb;
          border-radius: 12px;
          overflow: hidden;
        }
        .reason-label {
          background: #f8d7da;
          color: #721c24;
          padding: 0.75rem 1.25rem;
          font-weight: 600;
          font-size: 0.9rem;
        }
        .reason-content {
          padding: 1.25rem;
        }
        .reason-line {
          margin-bottom: 0.5rem;
          color: #555;
          font-size: 0.95rem;
          line-height: 1.8;
        }
        .reason-line:last-child {
          margin-bottom: 0;
        }
        /* 底部操作 */
        .detail-card-footer {
          padding: 1.25rem 2rem;
          background: #fafafa;
          border-top: 1px solid #eee;
          text-align: center;
        }
        /* 返回按钮 */
        .btn-submit {
          background: linear-gradient(135deg, #00C897, #00A87A);
          border: none;
          color: white;
          font-size: 1rem;
          font-weight: 600;
          padding: 0.7rem 2rem;
          border-radius: 30px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(0, 200, 151, 0.3);
        }
        .btn-submit:hover {
          background: linear-gradient(135deg, #00B386, #00936A);
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 200, 151, 0.4);
          color: white;
        }
        @media (max-width: 576px) {
          .detail-card-header {
            padding: 1.5rem 1.25rem 1rem;
          }
          .detail-card-title {
            font-size: 1.5rem;
          }
          .detail-card-body {
            padding: 1.25rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ApplicationDetail;

