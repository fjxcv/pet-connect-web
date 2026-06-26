/**
 * @file RescueDetail.js
 * @module PawRescue
 * @description 页面组件：RescueDetail。
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { rescueAPI } from '../api/api';
import { RESCUE_STATUS } from '../constants/site';
// 完整状态流转路径
const FULL_FLOW = ['pending_rescue', 'in_medical', 'recovering', 'awaiting_adoption', 'rescued'];
// 状态元信息（含义 + 预计停留时长）
const STATUS_META = {
  pending_rescue:  { desc: '救助信息已上报，等待救助人响应', duration: '1-3天' },
  in_medical:      { desc: '动物正在接受医疗救治', duration: '7-30天' },
  recovering:      { desc: '治疗完成，正在恢复健康', duration: '7-14天' },
  awaiting_adoption: { desc: '康复完毕，等待领养人', duration: '7-60天' },
  rescued:         { desc: '已被领养或妥善安置', duration: '—' },
  abandoned:       { desc: '救助流程已终止', duration: '—' },
};
// 状态颜色
const STATUS_COLOR = {
  pending_rescue: 'secondary', in_medical: 'warning', recovering: 'info',
  awaiting_adoption: 'primary', rescued: 'success', abandoned: 'dark',
};
// 格式化日期时间 "2026.5.21 10:23"
const formatDateTime = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};
const RescueDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [stageRecords, setStageRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeStatus, setActiveStatus] = useState(null);
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [caseRes, recordsRes] = await Promise.all([
        rescueAPI.getById(id),
        rescueAPI.getStageRecords(id),
      ]);
      setCaseData(caseRes.data);
      const records = Array.isArray(recordsRes.data) ? recordsRes.data : [];
      setStageRecords(records);
    } catch (err) {
      setError('加载救助详情失败，请稍后重试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);
  useEffect(() => { fetchData(); }, [fetchData]);
  // 构建已达状态列表（从 status_logs 提取）
  const reachedStatuses = useMemo(() => {
    if (!caseData?.status_logs) return [];
    const seen = new Set();
    const reached = [];
    for (const log of caseData.status_logs) {
      if (log.to_status && !seen.has(log.to_status)) {
        seen.add(log.to_status);
        reached.push(log.to_status);
      }
    }
    return reached;
  }, [caseData]);
  // 当前所在状态索引
  const currentIdx = useMemo(() => {
    const cur = caseData?.current_status;
    return reachedStatuses.indexOf(cur);
  }, [caseData, reachedStatuses]);
  // 默认选中当前状态
  useEffect(() => {
    if (caseData?.current_status && !activeStatus) {
      setActiveStatus(caseData.current_status);
    }
  }, [caseData, activeStatus]);
  // 构建时间线：合并 status_logs 和 stage_records，按时间分组
  const timelineByStatus = useMemo(() => {
    const map = {};
    reachedStatuses.forEach((s) => { map[s] = []; });
    // 添加状态变更日志
    (caseData?.status_logs || []).forEach((log) => {
      if (log.to_status && log.remark) {
        const entry = {
          type: 'status_change',
          time: log.created_at,
          content: `状态变更为「${RESCUE_STATUS[log.to_status] || log.to_status}」：${log.remark === 'Case created' ? '被发现上报' : log.remark}`,
          operator: log.operator?.username,
        };
        if (!map[log.to_status]) map[log.to_status] = [];
        map[log.to_status].push(entry);
      }
    });
    // 添加阶段记录，按时间归属到对应状态
    // 构建状态时间段：[{status, start, end}, ...]
    const periods = [];
    const logs = caseData?.status_logs || [];
    for (let i = 0; i < logs.length; i++) {
      const start = logs[i].created_at;
      const end = i + 1 < logs.length ? logs[i + 1].created_at : null; // null = 至今
      periods.push({ status: logs[i].to_status, start, end });
    }
    stageRecords.forEach((record) => {
      const t = record.created_at;
      // 找到 record 时间所属的状态
      let belonged = null;
      for (let i = periods.length - 1; i >= 0; i--) {
        const p = periods[i];
        if (t >= p.start && (!p.end || t < p.end)) {
          belonged = p.status;
          break;
        }
      }
      if (belonged) {
        const entry = {
          type: 'stage_record',
          time: record.created_at,
          content: record.content,
          operator: record.operator?.username,
        };
        if (!map[belonged]) map[belonged] = [];
        map[belonged].push(entry);
      }
    });
    // 每组按时间排序
    Object.keys(map).forEach((key) => {
      map[key].sort((a, b) => new Date(a.time) - new Date(b.time));
    });
    return map;
  }, [caseData, stageRecords, reachedStatuses]);
  // 加载中
  if (loading) {
    return (
      <div className="py-3 text-center">
        <div className="spinner-border text-success" role="status"></div>
        <p className="mt-2 text-muted">加载中...</p>
      </div>
    );
  }
  // 加载失败
  if (error) {
    return (
      <div className="py-3">
        <div className="alert alert-danger">{error}</div>
        <div className="text-center mt-3">
          <button className="btn btn-outline-success" onClick={() => navigate('/rescue/search')}>
            <i className="fas fa-arrow-left me-1"></i>返回
          </button>
        </div>
      </div>
    );
  }
  return (
    <div className="py-3">
      {/* 顶部导航 */}
      <div className="d-flex align-items-center gap-2 mb-3">
        <button className="btn btn-outline-secondary btn-sm" onClick={() => navigate(-1)}>
          <i className="fas fa-arrow-left me-1"></i>返回
        </button>
        <span className="fw-bold">{caseData?.rescue_no}</span>
      </div>
      {/* 状态流转路径 */}
      <div className="mb-4 text-start" style={{ fontSize: '1.15rem' }}>
        <span className="text-muted">救助进度：</span>
        {reachedStatuses.map((s, i) => (
          <React.Fragment key={s}>
            {i > 0 && <span className="text-muted mx-1">-&gt;</span>}
            <span
              style={{ cursor: 'pointer', fontWeight: s === caseData?.current_status ? 'bold' : 'normal' }}
              title={(() => {
                const meta = STATUS_META[s] || {};
                // 当前状态：显示含义 + 预计停留；已过去或终态：只显示含义
                if (s === caseData?.current_status && s !== 'rescued') {
                  return `${meta.desc || ''} ｜ 预计停留：${meta.duration || ''}`;
                }
                return meta.desc || '';
              })()}
              onClick={() => setActiveStatus(s)}
            >
              {RESCUE_STATUS[s] || s}
            </span>
          </React.Fragment>
        ))}
      </div>
      {/* 状态节点标签 */}
      <div className="mb-3">
        <ul className="nav nav-pills">
          {reachedStatuses.map((s) => (
            <li className="nav-item" key={s}>
              <button
                className={`nav-link ${activeStatus === s ? 'active' : ''}`}
                style={{ cursor: 'pointer' }}
                onClick={() => setActiveStatus(s)}
                title={(() => {
                  const meta = STATUS_META[s] || {};
                  if (s === caseData?.current_status && s !== 'rescued') {
                    return `${meta.desc || ''} ｜ 预计停留：${meta.duration || ''}`;
                  }
                  return meta.desc || '';
                })()}
              >
                {RESCUE_STATUS[s] || s}
              </button>
            </li>
          ))}
        </ul>
      </div>
      {/* 当前选中状态的时间线 */}
      {activeStatus && (
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span>
              <i className="fas fa-clock me-2"></i>
              {RESCUE_STATUS[activeStatus] || activeStatus} 阶段记录
            </span>
            {activeStatus === caseData?.current_status && activeStatus !== 'rescued' && (
              <small className="text-muted">
                {STATUS_META[activeStatus]?.desc} ｜ 预计停留：{STATUS_META[activeStatus]?.duration}
              </small>
            )}
          </div>
          <div className="card-body">
            {(timelineByStatus[activeStatus] || []).length === 0 ? (
              <p className="text-muted text-center mb-0">该阶段暂无记录</p>
            ) : (
              <div className="timeline">
                {(timelineByStatus[activeStatus] || []).map((item, idx) => (
                  <div key={idx} className="d-flex mb-3 pb-3 border-bottom">
                    <div className="flex-shrink-0 me-3">
                      <div
                        className={`rounded-circle d-flex align-items-center justify-content-center ${
                          item.type === 'status_change' ? 'bg-warning' : 'bg-info'
                        }`}
                        style={{ width: 32, height: 32 }}
                      >
                        <i
                          className={`fas fa-${
                            item.type === 'status_change' ? 'exchange-alt' : 'clipboard-list'
                          } text-white`}
                          style={{ fontSize: '0.75rem' }}
                        ></i>
                      </div>
                    </div>
                    <div className="flex-grow-1 min-w-0">
                      <div className="d-flex justify-content-between align-items-start mb-1">
                        <small className="text-muted">
                          <i className="far fa-clock me-1"></i>
                          {formatDateTime(item.time)}
                        </small>
                        {item.operator && (
                          <small className="text-muted">
                            <i className="fas fa-user me-1"></i>
                            {item.operator}
                          </small>
                        )}
                      </div>
                      <p className="mb-0" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {item.content}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RescueDetail;

