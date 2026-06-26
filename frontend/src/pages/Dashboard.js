/**
 * @file Dashboard.js
 * @module PawRescue
 * @description 页面组件：Dashboard。
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { adoptAPI } from '../api/api';
import { ONLINE_STATUS } from '../constants/site';
const STATUS_BADGE = {
  pending: 'bg-warning text-dark',
  approved: 'bg-success',
  rejected: 'bg-danger',
  need_material: 'bg-info text-dark',
};
const SPECIES_LABELS = { dog: '狗', cat: '猫', bird: '鸟', rabbit: '兔', fish: '鱼', other: '其他' };
const formatAgeMonths = (months) => {
  if (months == null) return '未知';
  const m = Number(months);
  if (m < 12) return `${m}个月`;
  const y = Math.floor(m / 12);
  const r = m % 12;
  return r === 0 ? `${y}岁` : `${y}岁${r}个月`;
};
const Dashboard = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    if (!localStorage.getItem('token')) { navigate('/login'); return; }
    (async () => {
      try {
        setLoading(true);
        const res = await adoptAPI.getMy();
        setApplications(Array.isArray(res.data) ? res.data : res.data.results || []);
      } catch (err) {
        setError('加载领养申请失败，请稍后重试。');
        console.error(err);
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);
  const getStatusBadge = (status) => {
    const label = ONLINE_STATUS[status] || status || '未知';
    const badge = STATUS_BADGE[status] || 'bg-secondary';
    return <span className={`badge ${badge}`}>{label}</span>;
  };
  if (loading) return (
    <div className="text-center py-5">
      <div className="spinner-border text-primary" role="status"></div>
      <p className="mt-2">加载中...</p>
    </div>
  );
  if (error) return <div className="alert alert-danger">{error}</div>;
  return (
    <div className="container py-4">
      <h2 className="mb-4"><i className="fas fa-tachometer-alt me-2"></i>我的领养</h2>
      <div className="row">
        <div className="col-md-8">
          <div className="card shadow-sm">
            <div className="card-header"><h5 className="mb-0">领养申请记录</h5></div>
            <div className="card-body">
              {applications.length === 0 ? (
                <p className="text-muted mb-0">暂无领养申请。去 <a href="/pets">领养宠物</a> 页面提交申请吧。</p>
              ) : (
                <div className="list-group list-group-flush">
                  {applications.map((app) => (
                    <div key={app.id} className="list-group-item px-0">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <h6 className="mb-1">{app.pet?.name || '未命名'}</h6>
                          {app.pet && (
                            <p className="mb-1 small text-muted">
                              {SPECIES_LABELS[app.pet.species] || app.pet.species} · {app.pet.breed || '未知'} · {formatAgeMonths(app.pet.age_months)}
                            </p>
                          )}
                          <p className="mb-1"><strong>留言：</strong>{app.message || '无'}</p>
                          {app.audit_opinion && <p className="mb-1 small"><strong>审核意见：</strong>{app.audit_opinion}</p>}
                          <small className="text-muted">申请时间：{app.created_at ? new Date(app.created_at).toLocaleDateString() : '-'}</small>
                        </div>
                        <div className="ms-3">{getStatusBadge(app.online_status)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card shadow-sm">
            <div className="card-header"><h5 className="mb-0">快捷操作</h5></div>
            <div className="card-body d-grid gap-2">
              <button type="button" className="btn btn-primary" onClick={() => navigate('/pets')}>浏览宠物</button>
              <button type="button" className="btn btn-outline-primary" onClick={() => navigate('/community')}>互动社区</button>
              <button type="button" className="btn btn-outline-secondary" onClick={() => navigate('/profile')}>个人资料</button>
            </div>
          </div>
          <div className="card shadow-sm mt-3">
            <div className="card-header"><h6 className="mb-0">状态说明</h6></div>
            <div className="card-body small">
              <p className="mb-1">{getStatusBadge('pending')} 待审核</p>
              <p className="mb-1">{getStatusBadge('approved')} 已通过</p>
              <p className="mb-1">{getStatusBadge('rejected')} 已拒绝</p>
              <p className="mb-0">{getStatusBadge('need_material')} 需补充材料</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

