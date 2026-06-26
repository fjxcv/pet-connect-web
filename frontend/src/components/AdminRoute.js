/**
 * @file AdminRoute.js
 * @module PawRescue
 * @description 后台路由守卫：校验登录与管理员身份后渲染子页面。
 */

import React, { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { authAPI } from '../api/api';

/**
 * 功能：判断用户是否为管理员（与后端 user_is_admin 逻辑一致）。
 * @param {Object|null} user - 当前用户对象
 * @returns {boolean}
 * 【权限】role===admin 或 is_staff/is_superuser 为 true。
 */
export const isAdminUser = (user) => {
  const role = user?.profile?.role;
  return role === 'admin' || user?.is_superuser || user?.is_staff;
};

/**
 * 功能：包裹 /admin 等后台页面，未登录跳转登录，非 admin 显示无权限提示。
 * @param {Object} props - children 为受保护页面
 * @returns {JSX.Element}
 * 【权限】visitor 跳转 /login；user 显示无权限；admin 渲染 children。
 */
const AdminRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!token);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await authAPI.getProfile();
        setUser(res.data);
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
        }
        setError(err.response?.data?.detail || '无法验证管理员权限');
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  // 【权限】游客无 token，跳转登录页
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status"></div>
        <p className="mt-2">正在验证管理员权限...</p>
      </div>
    );
  }
  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }
  // 【权限】已登录但非管理员
  if (!isAdminUser(user)) {
    return (
      <div className="alert alert-warning">
        您没有管理员权限。
        <Link to="/" className="ms-2">返回首页</Link>
      </div>
    );
  }
  return children;
};

export default AdminRoute;
