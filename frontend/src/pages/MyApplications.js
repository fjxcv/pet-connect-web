/**
 * @file MyApplications.js
 * @module PawRescue
 * @description 页面组件：MyApplications。
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { adoptAPI } from '../api/api';
// ===== 状态映射 =====
const getDisplayStatus = (app) => {
  const { online_status, verify_status } = app;
  if (online_status === 'pending') {
    return { label: '待审核', badge: 'warning' };
  }
  if (online_status === 'rejected') {
    return { label: '审核拒绝', badge: 'danger' };
  }
  if (online_status === 'need_material') {
    return { label: '待补充材料', badge: 'warning' };
  }
  if (online_status === 'approved') {
    if (verify_status === 'scheduled') {
      return { label: '待核验', badge: 'warning' };
    }
    if (verify_status === 'passed') {
      return { label: '核验通过', badge: 'success' };
    }
    if (verify_status === 'failed') {
      return { label: '核验失败', badge: 'danger' };
    }
    // 审核通过但尚未进入核验阶段
    return { label: '审核通过', badge: 'success' };
  }
  return { label: online_status || '未知', badge: 'secondary' };
};
// 格式化时间：年.月.日 时:分
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
const PAGE_SIZE = 10;
const MyApplications = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    const fetchApplications = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await adoptAPI.getMy();
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        setApplications(data);
      } catch (err) {
        setError('加载申请记录失败，请稍后重试。');
        console.error('Error fetching applications:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchApplications();
  }, [navigate]);
  // ===== 分页逻辑 =====
  const totalPages = Math.max(1, Math.ceil(applications.length / PAGE_SIZE));
  const startIdx = (currentPage - 1) * PAGE_SIZE;
  const pagedData = applications.slice(startIdx, startIdx + PAGE_SIZE);
  // 当数据变化时重置到第1页
  useEffect(() => {
    setCurrentPage(1);
  }, [applications.length]);
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };
  // 生成分页按钮
  const renderPagination = () => {
    if (totalPages <= 1) return null;
    const pages = [];
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage + 1 < maxVisible) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return (
      <nav className="mt-4" aria-label="分页导航">
        <ul className="pagination justify-content-center">
          <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
            <button className="page-link" onClick={() => goToPage(currentPage - 1)}>
              <i className="fas fa-chevron-left"></i>
            </button>
          </li>
          {startPage > 1 && (
            <>
              <li className="page-item">
                <button className="page-link" onClick={() => goToPage(1)}>1</button>
              </li>
              {startPage > 2 && <li className="page-item disabled"><span className="page-link">…</span></li>}
            </>
          )}
          {pages.map((p) => (
            <li key={p} className={`page-item ${p === currentPage ? 'active' : ''}`}>
              <button className="page-link" onClick={() => goToPage(p)}>{p}</button>
            </li>
          ))}
          {endPage < totalPages && (
            <>
              {endPage < totalPages - 1 && <li className="page-item disabled"><span className="page-link">…</span></li>}
              <li className="page-item">
                <button className="page-link" onClick={() => goToPage(totalPages)}>{totalPages}</button>
              </li>
            </>
          )}
          <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
            <button className="page-link" onClick={() => goToPage(currentPage + 1)}>
              <i className="fas fa-chevron-right"></i>
            </button>
          </li>
        </ul>
      </nav>
    );
  };
  // ===== 渲染 =====
  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
        <p className="mt-2">正在加载申请记录...</p>
      </div>
    );
  }
  return (
    <div className="my-applications-page">
      {/* ===== 面包屑导航 ===== */}
      <div className="detail-breadcrumb">
        <div className="container">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb mb-0">
              <li className="breadcrumb-item"><Link to="/">首页</Link></li>
              <li className="breadcrumb-item"><Link to="/pets">领养列表</Link></li>
              <li className="breadcrumb-item active" aria-current="page">我的申请与核验</li>
            </ol>
          </nav>
        </div>
      </div>
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-lg-10 col-xl-9">
            {/* 页面标题 */}
            <div className="page-header mb-4">
              <h3 className="page-title mb-0">
                <i className="fas fa-clipboard-list me-2 text-success"></i>
                我的申请与核验
              </h3>
              <small className="text-muted">
                共 <strong>{applications.length}</strong> 条记录
              </small>
            </div>
            {/* 错误提示 */}
            {error && (
              <div className="alert alert-danger">
                <i className="fas fa-exclamation-circle me-2"></i>{error}
              </div>
            )}
            {/* 空状态 */}
            {!loading && !error && applications.length === 0 && (
              <div className="empty-state text-center py-5">
                <div className="empty-icon mb-3">
                  <i className="fas fa-inbox fa-4x text-muted"></i>
                </div>
                <h5 className="text-muted mb-2">暂无申请记录</h5>
                <p className="text-muted small mb-4">您还没有提交过任何领养申请。</p>
                <Link to="/pets" className="btn btn-success">
                  <i className="fas fa-paw me-2"></i>去浏览宠物
                </Link>
              </div>
            )}
            {/* 申请列表表格 */}
            {applications.length > 0 && (
              <div className="table-card">
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th className="col-pet">宠物名</th>
                        <th className="col-status">审核/核验状态</th>
                        <th className="col-time">提交审核/核验时间</th>
                        <th className="col-action"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {pagedData.map((app) => {
                        const status = getDisplayStatus(app);
                        const showDetail = status.label === '审核拒绝' || status.label === '核验失败';
                        return (
                          <tr key={app.id}>
                            <td>
                              <div className="pet-name-cell">
                                <img
                                  src={app.pet?.photo_url || 'https://via.placeholder.com/40x40?text=Pet'}
                                  className="pet-thumb"
                                  alt={app.pet?.name || '宠物'}
                                  onError={(e) => {
                                    e.target.src = 'https://via.placeholder.com/40x40?text=Pet';
                                  }}
                                />
                                <span className="pet-name-text">{app.pet?.name || '未知宠物'}</span>
                              </div>
                            </td>
                            <td>
                              <span className={`badge badge-status bg-${status.badge} ${status.badge === 'warning' ? 'text-dark' : ''}`}>
                                {status.label}
                              </span>
                            </td>
                            <td className="text-muted">{formatDateTime(app.created_at)}</td>
                            <td className="text-end">
                              {showDetail && (
                                <Link
                                  to={`/my-applications/${app.id}`}
                                  className="btn btn-outline-secondary btn-sm"
                                >
                                  查看详情
                                </Link>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                {/* 分页信息 */}
                <div className="table-footer">
                  <small className="text-muted">
                    显示第 {startIdx + 1}–{Math.min(startIdx + PAGE_SIZE, applications.length)} 条，
                    共 {applications.length} 条记录
                  </small>
                </div>
              </div>
            )}
            {/* 分页组件 */}
            {renderPagination()}
            {/* 返回按钮 */}
            {applications.length > 0 && (
              <div className="text-center mt-4">
                <Link to="/pets" className="btn btn-submit px-5">
                  <i className="fas fa-arrow-left me-2"></i>返回
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* ===== 样式 ===== */}
      <style>{`
        .my-applications-page {
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
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        .page-title {
          font-size: 1.4rem;
          font-weight: 600;
          color: #333;
        }
        /* 表格卡片 */
        .table-card {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .table thead th {
          background: #f8f9fa;
          border-bottom: 2px solid #e9ecef;
          font-weight: 600;
          color: #555;
          font-size: 0.9rem;
          padding: 1rem 1.25rem;
          white-space: nowrap;
        }
        .table tbody td {
          padding: 1rem 1.25rem;
          vertical-align: middle;
          border-bottom: 1px solid #f0f0f0;
        }
        .table tbody tr:last-child td {
          border-bottom: none;
        }
        .table tbody tr:hover {
          background-color: #f8fffd;
        }
        .col-pet { width: 30%; }
        .col-status { width: 22%; }
        .col-time { width: 30%; }
        .col-action { width: 18%; }
        /* 宠物名单元格 */
        .pet-name-cell {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        .pet-thumb {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          object-fit: cover;
          flex-shrink: 0;
          border: 1px solid #eee;
        }
        .pet-name-text {
          font-weight: 600;
          color: #333;
        }
        /* 状态标签 */
        .badge-status {
          font-size: 0.82rem;
          padding: 0.4em 0.85em;
          border-radius: 20px;
          font-weight: 500;
        }
        /* 表格底部信息 */
        .table-footer {
          padding: 0.75rem 1.25rem;
          background: #fafafa;
          border-top: 1px solid #eee;
        }
        /* 分页 */
        .pagination .page-link {
          color: #00C897;
          border-radius: 8px;
          margin: 0 2px;
          border: 1px solid #e0e0e0;
          transition: all 0.2s ease;
        }
        .pagination .page-link:hover {
          background: #e9f7f2;
          border-color: #00C897;
        }
        .pagination .page-item.active .page-link {
          background: #00C897;
          border-color: #00C897;
          color: white;
        }
        .pagination .page-item.disabled .page-link {
          color: #ccc;
          pointer-events: none;
        }
        /* 空状态 */
        .empty-state {
          background: white;
          border-radius: 16px;
          padding: 3rem 2rem;
          box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        /* 返回按钮 */
        .btn-submit {
          background: linear-gradient(135deg, #00C897, #00A87A);
          border: none;
          color: white;
          font-size: 1.05rem;
          font-weight: 600;
          padding: 0.75rem 2rem;
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
        /* 响应式 */
        @media (max-width: 768px) {
          .table thead th,
          .table tbody td {
            padding: 0.75rem 0.5rem;
            font-size: 0.85rem;
          }
          .pet-thumb {
            width: 32px;
            height: 32px;
          }
        }
      `}</style>
    </div>
  );
};

export default MyApplications;

