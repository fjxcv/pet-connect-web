/**
 * @file ModerationReasonModal.js
 * @module PawRescue
 * @description 可复用组件：ModerationReasonModal。
 */

import React, { useState } from 'react';
const ModerationReasonModal = ({
  show,
  title,
  targetLabel,
  actionLabel,
  onConfirm,
  onCancel,
  submitting,
}) => {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const handleClose = () => {
    setReason('');
    setError('');
    onCancel();
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = reason.trim();
    if (trimmed.length < 4) {
      setError('请填写至少 4 个字的处置原因');
      return;
    }
    setError('');
    onConfirm(trimmed);
  };
  if (!show) return null;
  return (
    <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <form onSubmit={handleSubmit}>
            <div className="modal-header">
              <h5 className="modal-title">{title || '管理操作确认'}</h5>
              <button type="button" className="btn-close" onClick={handleClose} aria-label="关闭" />
            </div>
            <div className="modal-body">
              {targetLabel && (
                <p className="small text-muted mb-2">对象：{targetLabel}</p>
              )}
              <label className="form-label">
                处置原因 <span className="text-danger">*</span>
              </label>
              <textarea
                className={`form-control ${error ? 'is-invalid' : ''}`}
                rows={3}
                value={reason}
                onChange={(e) => { setReason(e.target.value); setError(''); }}
                placeholder="请说明删除或封禁的原因，便于后续审计"
                autoFocus
              />
              {error && <div className="invalid-feedback d-block">{error}</div>}
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-outline-secondary" onClick={handleClose} disabled={submitting}>
                取消
              </button>
              <button type="submit" className="btn btn-danger" disabled={submitting}>
                {submitting ? '提交中...' : (actionLabel || '确认')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ModerationReasonModal;

