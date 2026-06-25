import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rescueAPI } from '../api/api';
import { SIZE_CATEGORY, HEALTH_STATUS } from '../constants/site';

const MY_RESCUES_KEY = 'pet_connect_my_rescues';

const loadMyRescues = () => {
  try {
    return JSON.parse(localStorage.getItem(MY_RESCUES_KEY) || '[]');
  } catch {
    return [];
  }
};

const getCurrentUserId = () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    return user?.id || null;
  } catch {
    return null;
  }
};

const saveMyRescues = (records) => {
  localStorage.setItem(MY_RESCUES_KEY, JSON.stringify(records));
};

// 去掉经纬度（格式如 "地址（30.123, 104.456）"）
const stripCoord = (addr) => {
  if (!addr) return addr;
  return addr.replace(/（\d+\.?\d*,\s*\d+\.?\d*）$/, '').trim();
};

// 根据新字段构建描述文本
const buildDescription = (item) => {
  const hasNewFields = item.size_category || item.health_status || item.nickname || item.contact;

  if (!hasNewFields) {
    return { narrative: item.appearance || '暂无描述', detail: '' };
  }

  const name = item.nickname || '某用户';
  const location = stripCoord(item.discover_address) || '某处';

  const narrative = `${name}在${location}发现一只流浪动物，待人前来救助...`;

  const parts = [];
  if (item.size_category) parts.push(`体型: ${SIZE_CATEGORY[item.size_category] || item.size_category}`);
  if (item.health_status) parts.push(`健康: ${HEALTH_STATUS[item.health_status] || item.health_status}`);
  parts.push(`怕人: ${item.afraid_of_people ? '是' : '否'}`);

  const detail = '详情：' + parts.join('，');

  return { narrative, detail };
};

const RescueList = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [helpingId, setHelpingId] = useState(null);
  const [contactModal, setContactModal] = useState(null); // 存 item，含 contact 字段

  const fetchCases = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const currentMyRescues = loadMyRescues();
      const helpedIds = new Set(currentMyRescues.map((r) => r.id));
      // 获取所有活跃状态的救助案例（待救助、医疗中、康复中）
      const res = await rescueAPI.getAll({
        status: 'pending_rescue,in_medical,recovering',
      });
      const list = Array.isArray(res.data) ? res.data : (res.data.results || []);
      // 过滤掉已救助过的；自己上报的也保留展示（但不能对自己点"救助"）
      setCases(
        list.filter((c) => !helpedIds.has(c.id)),
      );
    } catch (err) {
      setError('加载救助记录失败，请稍后重试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const formatTime = (iso) => {
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const handleHelp = async (item) => {
    setHelpingId(item.id);
    try {
      await rescueAPI.help(item.id);
      // 成功后弹窗展示联系方式
      setHelpingId(null);
      setContactModal(item);
      setCases((prev) => prev.filter((c) => c.id !== item.id));
      const currentMyRescues = loadMyRescues();
      const updated = [item, ...currentMyRescues.filter((r) => r.id !== item.id)];
      saveMyRescues(updated);
    } catch (err) {
      console.error(err);
      setHelpingId(null);
    }
  };

  const handleConfirmContact = () => {
    setContactModal(null);
  };

  return (
    <div className="py-3" style={{ minHeight: 'calc(100vh - 160px)' }}>
      {/* 顶部：标题 + 三个功能入口按钮 */}
      <div className="d-flex justify-content-between align-items-center mb-5 flex-wrap gap-2">
        <h2 className="mb-0">
          <i className="fas fa-hand-holding-heart me-2 text-success"></i>救助追踪
        </h2>
        <div className="d-flex gap-2">
          <button className="btn btn-outline-success" type="button" title="查看我救助的记录" onClick={() => navigate('/my-rescues')}>
            <i className="fas fa-list-check me-1"></i>我的救助
          </button>
          <button className="btn btn-outline-success" type="button" title="上报新的救助信息" onClick={() => navigate('/rescue/report')}>
            <i className="fas fa-plus me-1"></i>上报
          </button>
          <button className="btn btn-outline-success" type="button" title="查询救助记录" onClick={() => navigate('/rescue/search')}>
            <i className="fas fa-search me-1"></i>查询
          </button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-success" role="status"></div>
          <p className="mt-2 text-muted">加载中...</p>
        </div>
      )}

      {error && (
        <div className="alert alert-danger d-flex align-items-center gap-2">
          <i className="fas fa-exclamation-triangle"></i>
          <span>{error}</span>
          <button className="btn btn-outline-danger btn-sm ms-auto" onClick={fetchCases}>
            重试
          </button>
        </div>
      )}

      {!loading && !error && cases.length === 0 && (
        <div className="text-center py-5">
          <i className="fas fa-inbox fa-3x text-muted mb-3 d-block"></i>
          <p className="text-muted">
            暂无上报记录，点击上方上报按钮发布第一条救助信息。
          </p>
        </div>
      )}

      {!loading && !error && cases.length > 0 && (
        <div className="row">
          <div className="col-lg-8 mx-auto">
            <div className="list-group">
              {cases.map((item) => {
                const { narrative, detail } = buildDescription(item);
                return (
                  <div
                    key={item.id}
                    className={`list-group-item p-0 ${helpingId === item.id ? 'opacity-50' : ''}`}
                    style={{ transition: 'opacity 0.3s ease', borderLeft: 'none', borderRight: 'none' }}
                  >
                    <div className="d-flex" style={{ minHeight: 140 }}>
                      <div className="flex-shrink-0" style={{ width: 140, minHeight: 140 }}>
                        {item.photo_urls?.[0] ? (
                          <img
                            src={item.photo_urls[0]}
                            alt=""
                            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                          />
                        ) : (
                          <div
                            className="d-flex align-items-center justify-content-center bg-light"
                            style={{ width: '100%', height: '100%' }}
                          >
                            <i className="fas fa-paw fa-3x text-muted"></i>
                          </div>
                        )}
                      </div>

                      <div className="flex-grow-1 d-flex flex-column justify-content-center px-3 py-2 min-w-0" style={{ overflow: 'hidden' }}>
                        <p className="mb-1" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflowWrap: 'break-word', lineHeight: 1.6 }}>
                          {narrative}
                        </p>
                        {detail && (
                          <p className="mb-1 text-muted" style={{ fontSize: '0.85rem', wordBreak: 'break-word', overflowWrap: 'break-word', lineHeight: 1.5 }}>
                            {detail}
                          </p>
                        )}
                        <small className="text-muted mt-1">
                          救助编号：{item.rescue_no} · 发布于{formatTime(item.created_at)}
                        </small>
                      </div>

                      <div className="flex-shrink-0 d-flex flex-column justify-content-end align-items-end px-2 py-2" style={{ minWidth: 80 }}>
                        {item.reporter?.id === getCurrentUserId() ? (
                          <span className="badge bg-secondary">我的上报</span>
                        ) : (
                          <button
                            className="btn btn-success btn-sm"
                            type="button"
                            onClick={() => handleHelp(item)}
                            disabled={helpingId === item.id}
                          >
                            救助
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* 联系方式弹窗 */}
      {contactModal && (
        <div className="modal d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header border-0 pb-0">
                <h5 className="modal-title">
                  <i className="fas fa-check-circle text-success me-2"></i>已成功响应救助
                </h5>
              </div>
              <div className="modal-body pt-3">
                <p className="mb-2">您可以联系上报人确认动物具体位置：</p>
                <p className="mb-3">
                  <strong>联系方式（手机号/微信号）：</strong>
                  <span className="text-primary">{contactModal.contact || '未填写'}</span>
                </p>
                <p className="text-muted mb-0" style={{ fontSize: '0.85rem' }}>
                  <i className="fas fa-info-circle me-1"></i>
                  请仅用于本次救助沟通，勿将信息转告他人或用于其他用途。
                </p>
              </div>
              <div className="modal-footer border-0 pt-0">
                <button
                  className="btn btn-success"
                  onClick={handleConfirmContact}
                >
                  确认
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RescueList;
