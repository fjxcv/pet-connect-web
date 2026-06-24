import React from 'react';
import { Link } from 'react-router-dom';
import { useManageMode } from '../context/ManageModeContext';

const AdminManageBar = ({ userId, onEdit, onHide, onPublish, onDelete, onBanUser, extra, compact }) => {
  const { canManage } = useManageMode();
  if (!canManage) return null;

  return (
    <div className={`alert alert-warning py-2 px-3 mb-2 d-flex flex-wrap align-items-center gap-2 small ${compact ? 'flex-nowrap' : ''}`}>
      <span className="fw-semibold text-nowrap"><i className="fas fa-shield-alt me-1" />管理</span>
      {onEdit && (
        <button type="button" className="btn btn-outline-primary btn-sm" onClick={onEdit}>编辑</button>
      )}
      {onHide && (
        <button type="button" className="btn btn-outline-secondary btn-sm" onClick={onHide}>下线</button>
      )}
      {onPublish && (
        <button type="button" className="btn btn-outline-success btn-sm" onClick={onPublish}>重新上线</button>
      )}
      {onDelete && (
        <button type="button" className="btn btn-outline-danger btn-sm" onClick={onDelete}>删除</button>
      )}
      {userId && (
        <>
          <Link to={`/users/${userId}`} className="btn btn-outline-info btn-sm">用户主页</Link>
          {onBanUser && (
            <button type="button" className="btn btn-outline-dark btn-sm" onClick={onBanUser}>封禁</button>
          )}
        </>
      )}
      {extra}
    </div>
  );
};

export default AdminManageBar;
