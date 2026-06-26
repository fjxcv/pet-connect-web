/**
 * @file AdminManageBar.js
 * @module PawRescue
 * @description 前台管理工具条：切换管理模式后的编辑/下线/封禁等快捷操作。
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useManageMode } from '../context/ManageModeContext';

/**
 * 功能：在列表/详情页顶部显示管理操作按钮。
 * @param {Object} props
 * @param {number} [props.userId] - 关联用户 ID，显示用户主页与封禁
 * @param {Function} [props.onEdit] - 编辑回调
 * @param {Function} [props.onHide] - 下线回调
 * @param {Function} [props.onPublish] - 重新上线回调
 * @param {Function} [props.onDelete] - 删除回调
 * @param {Function} [props.onBanUser] - 封禁用户回调
 * @param {React.ReactNode} [props.extra] - 额外按钮
 * @param {boolean} [props.compact] - 紧凑布局
 * @returns {JSX.Element|null}
 * 【权限】仅 canManage（admin 且 manageMode 开启）时渲染；visitor/user 返回 null。
 */
const AdminManageBar = ({ userId, onEdit, onHide, onPublish, onDelete, onBanUser, extra, compact }) => {
  const { canManage } = useManageMode();
  // 【权限】非管理模式不显示工具条
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
