/**
 * @file MyRescues.js
 * @module PawRescue
 * @description 页面组件：MyRescues。
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rescueAPI } from '../api/api';
import { RESCUE_STATUS } from '../constants/site';
// 状态对应的颜色标签
const STATUS_COLOR = {
  pending_rescue: 'secondary',
  in_medical: 'warning',
  recovering: 'info',
  awaiting_adoption: 'primary',
  rescued: 'success',
  abandoned: 'dark',
};
// 格式化日期为 "年.月.日"
const formatDate = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`;
};
const MyRescues = () => {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const fetchHelped = useCallback(async (pageNum, filter) => {
    try {
      setLoading(true);
      setError(null);
      const params = { page: pageNum };
      if (filter) params.status = filter;
      const res = await rescueAPI.getHelpedCases(params);
      // DRF 分页返回格式
      if (res.data.results) {
        setRecords(res.data.results);
        setTotalCount(res.data.count);
        const pages = Math.ceil(res.data.count / 10);
        setTotalPages(pages || 1);
      } else {
        setRecords(res.data);
        setTotalCount(res.data.length);
        setTotalPages(1);
      }
    } catch (err) {
      setError('加载我的救助记录失败。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    fetchHelped(page, statusFilter);
  }, [page, statusFilter, fetchHelped]);
  const handleFilterChange = (e) => {
    setStatusFilter(e.target.value);
    setPage(1);
  };
  const handleReset = () => {
    setStatusFilter('');
    setPage(1);
  };
  // 是否显示"更新状态"按钮（救助成功和已终止不显示）
  const showUpdateBtn = (status) => status !== 'rescued' && status !== 'abandoned';
  return (
    <div className="d-flex flex-column py-3" style={{ minHeight: 'calc(100vh - 160px)' }}>
      {/* 顶部标题 */}
      <h2 className="mb-4">
        <i className="fas fa-heart me-2 text-success"></i>我的救助
      </h2>
      {/* 筛选栏 */}
      <div className="d-flex align-items-center gap-2 mb-4 flex-wrap">
        <label className="form-label mb-0 fw-bold">按状态筛选：</label>
        <select
          className="form-select"
          style={{ width: 'auto', minWidth: 160 }}
          value={statusFilter}
          onChange={handleFilterChange}
        >
          <option value="">全部状态</option>
          {Object.entries(RESCUE_STATUS)
            .filter(([key]) => key !== 'pending_rescue' && key !== 'abandoned')
            .map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
        </select>
        <button className="btn btn-outline-secondary btn-sm" onClick={handleReset}>
          <i className="fas fa-redo me-1"></i>重置
        </button>
      </div>
      {/* 加载中 */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-success" role="status"></div>
          <p className="mt-2 text-muted">加载中...</p>
        </div>
      )}
      {/* 错误提示 */}
      {error && (
        <div className="alert alert-danger d-flex align-items-center gap-2">
          <i className="fas fa-exclamation-triangle"></i>
          <span>{error}</span>
          <button className="btn btn-outline-danger btn-sm ms-auto" onClick={() => fetchHelped(page, statusFilter)}>
            重试
          </button>
        </div>
      )}
      {/* 空状态 */}
      {!loading && !error && records.length === 0 && (
        <div className="text-center py-5">
          <i className="fas fa-inbox fa-3x text-muted mb-3 d-block"></i>
          <p className="text-muted">暂无救助动物记录。</p>
        </div>
      )}
      {/* 列表 */}
      {!loading && !error && records.length > 0 && (
        <>
        <div className="table-responsive">
          <table className="table table-hover align-middle table-sm" style={{ fontSize: '0.9rem' }}>
            <thead className="table-light">
              <tr>
                <th style={{ width: 85 }}>救助对象</th>
                <th style={{ width: 155 }}>救助编号</th>
                <th style={{ width: 100 }}>当前状态</th>
                <th style={{ width: 105 }}>救助日期</th>
                <th style={{ width: 160 }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {records.map((item) => (
                <tr key={item.id}>
                  {/* 救助对象照片缩略图 */}
                  <td className="text-center">
                    <div
                      className="rounded overflow-hidden d-inline-block"
                      style={{ width: 48, height: 48 }}
                    >
                      {item.photo_urls?.[0] ? (
                        <img
                          src={item.photo_urls[0]}
                          alt=""
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      ) : (
                        <div
                          className="d-flex align-items-center justify-content-center bg-light"
                          style={{ width: '100%', height: '100%' }}
                        >
                          <i className="fas fa-paw text-muted" style={{ fontSize: '0.8rem' }}></i>
                        </div>
                      )}
                    </div>
                  </td>
                  {/* 救助编号 */}
                  <td>
                    <span className="fw-bold" style={{ fontSize: '0.85rem' }}>{item.rescue_no}</span>
                  </td>
                  {/* 当前状态 */}
                  <td>
                    <span className={`badge bg-${STATUS_COLOR[item.current_status] || 'secondary'}`} style={{ fontSize: '0.75rem' }}>
                      {RESCUE_STATUS[item.current_status] || item.current_status}
                    </span>
                  </td>
                  {/* 救助日期 */}
                  <td>
                    <span style={{ fontSize: '0.85rem' }}>{formatDate(item.help_date || item.updated_at)}</span>
                  </td>
                  {/* 操作按钮 */}
                  <td>
                    <div className="d-flex gap-1 justify-content-center">
                      {showUpdateBtn(item.current_status) && (
                        <>
                          <button
                            className="btn btn-outline-success btn-sm"
                            type="button"
                            onClick={() => navigate(`/my-rescues/${item.id}/update-status`)}
                          >
                            更新状态
                          </button>
                          <button
                            className="btn btn-outline-info btn-sm"
                            type="button"
                            onClick={() => navigate(`/my-rescues/${item.id}/stage-record`)}
                          >
                            填写记录
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* 分页 */}
        {totalPages > 1 && (
          <div className="d-flex justify-content-center align-items-center gap-2 mt-4">
            <button
              className="btn btn-outline-secondary btn-sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <i className="fas fa-chevron-left me-1"></i>上一页
            </button>
            <span className="text-muted mx-2">
              第 {page}/{totalPages} 页（共 {totalCount} 条）
            </span>
            <button
              className="btn btn-outline-secondary btn-sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              下一页<i className="fas fa-chevron-right ms-1"></i>
            </button>
          </div>
        )}
        </>
      )}
      {/* 返回按钮：贴近白色区域底部 */}
      <div className="text-center mt-auto pt-4 pb-3">
        <button className="btn btn-outline-success" onClick={() => navigate('/rescue')}>
          <i className="fas fa-arrow-left me-1"></i>返回
        </button>
      </div>
    </div>
  );
};

export default MyRescues;

