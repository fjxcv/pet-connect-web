/**
 * @file auth.js
 * @module PawRescue
 * @description 工具函数：auth。
 */

export const logout = (navigate) => {
  localStorage.removeItem('token');
  if (navigate) {
    navigate('/');
  } else {
    window.location.href = '/';
  }
};

export const confirmLogout = (navigate) => {
  if (window.confirm('确定要退出登录吗？')) {
    logout(navigate);
  }
};

