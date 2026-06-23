import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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

// 状态流转规则：只能推进到下一个状态
const STATUS_NEXT = {
  in_medical: 'recovering',
  recovering: 'awaiting_adoption',
  awaiting_adoption: 'rescued',
};

const UpdateRescueStatus = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState(null);
  const [newStatus, setNewStatus] = useState(null);
  const [remark, setRemark] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [validationError, setValidationError] = useState('');

  // 加载救助案例数据
  const fetchCase = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await rescueAPI.getById(id);
      setCaseData(res.data);
    } catch (err) {
      setError('加载救助记录失败，请稍后重试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCase();
  }, [fetchCase]);

  // 切换状态到下一步
  const handleSwitch = () => {
    if (!caseData) return;
    const next = STATUS_NEXT[caseData.current_status];
    if (next) {
      setNewStatus(next);
      setValidationError('');
    }
  };

  // 提交更新
  const handleSubmit = async () => {
    setValidationError('');

    if (!newStatus) {
      setValidationError('请选择要更新的状态');
      return;
    }

    if (!remark.trim()) {
      setValidationError('请填写状态备注（诊断结果、治疗方案等）');
      return;
    }

    try {
      setSubmitting(true);
      await rescueAPI.updateStatus(id, {
        current_status: newStatus,
        remark: remark.trim(),
      });
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail || '更新失败，请重试。';
      setValidationError(detail);
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // 返回我的救助页
  const handleBack = () => {
    navigate('/my-rescues');
  };

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
        <div className="alert alert-danger d-flex align-items-center gap-2">
          <i className="fas fa-exclamation-triangle"></i>
          <span>{error}</span>
          <button className="btn btn-outline-danger btn-sm ms-auto" onClick={fetchCase}>
            重试
          </button>
        </div>
        <div className="text-center mt-3">
          <button className="btn btn-outline-success" onClick={handleBack}>
            <i className="fas fa-arrow-left me-1"></i>返回
          </button>
        </div>
      </div>
    );
  }

  const currentStatus = caseData?.current_status;
  const canSwitch = STATUS_NEXT[currentStatus] && !newStatus;
  const canSubmit = !!newStatus;

  // 更新成功
  if (success) {
    return (
      <div className="py-3">
        <div className="row">
          <div className="col-lg-6 mx-auto">
            <div className="text-center py-5">
              <i className="fas fa-check-circle fa-4x text-success mb-3 d-block"></i>
              <h4 className="mb-3">更新成功</h4>
              <p className="text-muted mb-4">
                救助编号 <strong>{caseData?.rescue_no}</strong> 的状态已更新为
                <span className={`badge bg-${STATUS_COLOR[newStatus] || 'secondary'} ms-2`}>
                  {RESCUE_STATUS[newStatus] || newStatus}
                </span>
              </p>
              <button className="btn btn-success" onClick={handleBack}>
                <i className="fas fa-arrow-left me-1"></i>返回
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-3">
      <div className="row">
        <div className="col-lg-6 mx-auto">
          {/* 标题栏：标题 + 切换状态按钮 */}
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h2 className="mb-0">
              <i className="fas fa-edit me-2 text-success"></i>更新状态
            </h2>
            {canSwitch && (
              <button
                className="btn btn-outline-success"
                type="button"
                onClick={handleSwitch}
                title="将会切换到下一个状态"
              >
                <i className="fas fa-exchange-alt me-1"></i>切换状态
              </button>
            )}
            {!canSwitch && newStatus && (
              <button
                className="btn btn-outline-secondary"
                type="button"
                disabled
                title="已经切换到下一个状态"
              >
                <i className="fas fa-check me-1"></i>已切换
              </button>
            )}
            {!STATUS_NEXT[currentStatus] && (
              <span className="text-muted" style={{ fontSize: '0.9rem' }}>
                <i className="fas fa-info-circle me-1"></i>当前状态不可变更
              </span>
            )}
          </div>

          <div className="card">
            <div className="card-body">
              {/* 救助编号 */}
              <div className="mb-3">
                <span className="text-muted">救助编号：</span>
                <span className="fw-bold">{caseData?.rescue_no}</span>
              </div>

              {/* 当前状态（只读） */}
              <div className="mb-3">
                <span className="text-muted">当前状态：</span>
                <span className={`badge bg-${STATUS_COLOR[currentStatus] || 'secondary'}`}>
                  {RESCUE_STATUS[currentStatus] || currentStatus}
                </span>
              </div>

              {/* 新状态 */}
              {newStatus && (
                <div className="mb-3">
                  <span className="text-muted">新状态：</span>
                  <span className={`badge bg-${STATUS_COLOR[newStatus] || 'secondary'}`}>
                    {RESCUE_STATUS[newStatus] || newStatus}
                  </span>
                  <i className="fas fa-arrow-right text-muted mx-2"></i>
                  <small className="text-success">即将更新</small>
                </div>
              )}

              {/* 状态备注（多行文本） */}
              <div className="mb-3">
                <label className="form-label fw-bold">
                  状态备注 <span className="text-danger">*</span>
                </label>
                <textarea
                  className="form-control"
                  rows={5}
                  placeholder="诊断结果、治疗方案、宠物现状..."
                  value={remark}
                  onChange={(e) => {
                    setRemark(e.target.value);
                    setValidationError('');
                  }}
                  disabled={submitting}
                ></textarea>
              </div>

              {/* 校验错误 */}
              {validationError && (
                <div className="alert alert-danger py-2 mb-3">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {validationError}
                </div>
              )}

              {/* 底部按钮 */}
              <div className="d-flex justify-content-center gap-2">
                <button
                  className="btn btn-success"
                  type="button"
                  onClick={handleSubmit}
                  disabled={submitting || !canSubmit}
                >
                  {submitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                      提交中...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-check me-1"></i>确认更新
                    </>
                  )}
                </button>
                <button
                  className="btn btn-outline-secondary"
                  type="button"
                  onClick={handleBack}
                  disabled={submitting}
                >
                  <i className="fas fa-arrow-left me-1"></i>返回
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UpdateRescueStatus;
