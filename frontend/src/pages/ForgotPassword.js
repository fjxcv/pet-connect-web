/**
 * @file ForgotPassword.js
 * @module PawRescue
 * @description 页面组件：ForgotPassword。
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/api';
const RESET_CODE_MAILBOX = '1714929806@qq.com';
const ForgotPassword = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    try {
      await authAPI.passwordResetRequest(email);
      setMessage(`验证码已发送至指定邮箱 ${RESET_CODE_MAILBOX}，请查收后在此输入验证码。`);
      setStep(2);
    } catch (err) {
      const detail = err.response?.data?.email?.[0] || err.response?.data?.detail || '发送失败，请检查邮箱是否注册或稍后重试。';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };
  const handleConfirmReset = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }
    if (newPassword.length < 8) {
      setError('密码长度至少 8 位');
      return;
    }
    setLoading(true);
    setError('');
    setMessage('');
    try {
      await authAPI.passwordResetConfirm({ email, code, new_password: newPassword });
      setMessage('密码重置成功，即将跳转至登录页...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const detail = err.response?.data?.non_field_errors?.[0]
        || err.response?.data?.detail
        || '重置失败，验证码可能已过期。';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="d-flex align-items-center justify-content-center py-5">
      <div className="card shadow-lg p-4 rounded-4" style={{ maxWidth: 420, width: '100%' }}>
        <div className="text-center mb-4">
          <i className="fas fa-key fa-2x text-success mb-3"></i>
          <h3 className="fw-bold">找回密码</h3>
          <p className="text-muted small">
            {step === 1
              ? '输入注册邮箱申请重置，验证码将发送至指定邮箱'
              : '输入验证码和新密码'}
          </p>
        </div>
        {error && <div className="alert alert-danger">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}
        {step === 1 ? (
          <form onSubmit={handleRequestReset}>
            <div className="mb-3">
              <label htmlFor="email" className="form-label">邮箱</label>
              <input
                type="email"
                id="email"
                className="form-control form-control-lg"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="请输入注册邮箱"
              />
            </div>
            <button type="submit" className="btn btn-success w-100 py-2" disabled={loading}>
              {loading ? '发送中...' : '发送验证码'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirmReset}>
            <div className="mb-3">
              <label className="form-label">邮箱</label>
              <input type="email" className="form-control" value={email} readOnly />
            </div>
            <div className="mb-3">
              <label htmlFor="code" className="form-label">验证码</label>
              <input
                type="text"
                id="code"
                className="form-control"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                placeholder="6 位验证码"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="newPassword" className="form-label">新密码</label>
              <input
                type="password"
                id="newPassword"
                className="form-control"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                placeholder="至少 8 位字符"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="confirmPassword" className="form-label">确认密码</label>
              <input
                type="password"
                id="confirmPassword"
                className="form-control"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                placeholder="再次输入新密码"
              />
            </div>
            <button type="submit" className="btn btn-success w-100 py-2 mb-2" disabled={loading}>
              {loading ? '重置中...' : '重置密码'}
            </button>
            <button type="button" className="btn btn-outline-secondary w-100" onClick={() => setStep(1)}>
              重新发送验证码
            </button>
          </form>
        )}
        <div className="text-center mt-3">
          <Link to="/login" className="text-decoration-none text-success">返回登录</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

