<<<<<<< HEAD
import React, { useState, useEffect } from 'react';
=======
import React, { useState } from 'react';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/api';

const ForgotPassword = () => {
  const navigate = useNavigate();
<<<<<<< HEAD
=======
  const [step, setStep] = useState(1);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
<<<<<<< HEAD
  const [countdown, setCountdown] = useState(0);
  const [sendingCode, setSendingCode] = useState(false);
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

<<<<<<< HEAD
  useEffect(() => {
    if (countdown <= 0) return undefined;
    const timer = setInterval(() => {
      setCountdown((prev) => Math.max(prev - 1, 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [countdown]);

  const requestCode = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('请先填写邮箱地址');
      return;
    }
    setSendingCode(true);
=======
  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    setError('');
    setMessage('');
    try {
      await authAPI.passwordResetRequest(email);
      setMessage('验证码已发送至您的邮箱，请查收。');
<<<<<<< HEAD
      setCountdown(60);
=======
      setStep(2);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    } catch (err) {
      const detail = err.response?.data?.email?.[0] || err.response?.data?.detail || '发送失败，请检查邮箱是否正确。';
      setError(detail);
    } finally {
<<<<<<< HEAD
      setSendingCode(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('请先填写邮箱地址');
      return;
    }
    if (!code.trim()) {
      setError('请输入验证码');
      return;
    }
=======
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
        || err.response?.data?.code?.[0]
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
          <p className="text-muted small">输入注册邮箱获取验证码并设置新密码</p>
=======
          <p className="text-muted small">
            {step === 1 ? '输入注册邮箱获取验证码' : '输入验证码和新密码'}
          </p>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}

<<<<<<< HEAD
        <form onSubmit={handleSubmit}>
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

          <div className="mb-3">
            <label htmlFor="code" className="form-label">验证码</label>
            <div className="d-flex gap-2">
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              <input
                type="text"
                id="code"
                className="form-control"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                placeholder="6 位验证码"
              />
<<<<<<< HEAD
              <button
                type="button"
                className="btn btn-outline-success"
                onClick={requestCode}
                disabled={sendingCode || countdown > 0}
                style={{ minWidth: 140 }}
              >
                {countdown > 0 ? `${countdown}s` : '发送验证码'}
              </button>
            </div>
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
        </form>
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

        <div className="text-center mt-3">
          <Link to="/login" className="text-decoration-none text-success">返回登录</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
