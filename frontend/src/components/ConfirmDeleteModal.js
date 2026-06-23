import React from 'react';

const ConfirmDeleteModal = ({
  visible,
  title = '确认删除',
  message,
  onConfirm,
  onClose,
  cancelLabel = '取消',
  confirmLabel = '确认删除',
  loading = false,
}) => {
  if (!visible) {
    return null;
  }

  return (
    <div
      className="modal fade show d-block"
      tabIndex="-1"
      role="dialog"
      style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}
    >
      <div className="modal-dialog modal-dialog-centered" role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{title}</h5>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
          </div>
          <div className="modal-body">
            <p>{message}</p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              {cancelLabel}
            </button>
            <button
              type="button"
              className="btn btn-danger"
              onClick={onConfirm}
              disabled={loading}
            >
              {loading ? '删除中...' : confirmLabel}
            </button>
          </div>
        </div>
      </div>
      <style>{`
        .modal-content {
          border-radius: 1rem;
          overflow: hidden;
        }

        .modal-body p {
          margin-bottom: 0;
          color: #374151;
          line-height: 1.7;
        }

        .modal-header {
          border-bottom: 1px solid #e9ecef;
        }

        .modal-footer {
          border-top: 1px solid #e9ecef;
          /* 核心：按钮居中 */
          justify-content: center;
          gap: 12px;
        }

        .btn-danger {
          min-width: 110px;
        }
      `}</style>
    </div>
  );
};

export default ConfirmDeleteModal;
