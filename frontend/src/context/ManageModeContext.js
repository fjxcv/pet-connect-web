/**
 * @file ManageModeContext.js
 * @module PawRescue
 * @description 管理员模式上下文：控制前台管理工具条可见性与 canManage 状态。
 */

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authAPI } from '../api/api';
import { isAdminUser } from '../components/AdminRoute';

/** 默认上下文值 */
const ManageModeContext = createContext({
  isAdmin: false,
  manageMode: false,
  canManage: false,
  setManageMode: () => {},
  refreshAdmin: () => {},
});

/**
 * 功能：提供管理员身份与管理模式开关（持久化到 localStorage）。
 * 【权限】仅 admin 可将 manageMode 设为 true，从而 canManage=true。
 * @param {Object} props - React 子节点
 * @returns {JSX.Element}
 */
export const ManageModeProvider = ({ children }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [manageMode, setManageModeState] = useState(
    () => localStorage.getItem('manageMode') === '1',
  );

  /**
   * 功能：根据 token 拉取用户资料并刷新 isAdmin 状态。
   * 【权限】visitor 无 token 时 isAdmin=false。
   */
  const refreshAdmin = useCallback(async () => {
    const token = localStorage.getItem('token');
    // 【权限】未登录不是管理员
    if (!token) {
      setIsAdmin(false);
      return;
    }
    try {
      const res = await authAPI.getProfile();
      setIsAdmin(isAdminUser(res.data));
    } catch {
      setIsAdmin(false);
    }
  }, []);

  useEffect(() => {
    refreshAdmin();
    const onStorage = () => refreshAdmin();
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [refreshAdmin]);

  /** 功能：切换管理模式并写入 localStorage。【权限】通常仅 admin 会调用 */
  const setManageMode = useCallback((on) => {
    setManageModeState(on);
    localStorage.setItem('manageMode', on ? '1' : '0');
  }, []);

  const value = useMemo(
    () => ({
      isAdmin,
      manageMode,
      // canManage：管理员且已开启管理模式，前台才显示编辑/下线等按钮
      canManage: isAdmin && manageMode,
      setManageMode,
      refreshAdmin,
    }),
    [isAdmin, manageMode, setManageMode, refreshAdmin],
  );

  return (
    <ManageModeContext.Provider value={value}>
      {children}
    </ManageModeContext.Provider>
  );
};

/**
 * 功能：读取管理模式上下文。
 * @returns {{ isAdmin: boolean, manageMode: boolean, canManage: boolean, setManageMode: Function, refreshAdmin: Function }}
 * 【权限】canManage = isAdmin && manageMode，用于前台内容管理按钮显隐。
 */
export const useManageMode = () => useContext(ManageModeContext);
