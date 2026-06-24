# -*- coding: utf-8 -*-
"""Rewrite auth-related frontend pages as UTF-8 using unicode escapes."""
from __future__ import annotations

import os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')

LOGIN = r'''import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/api';
import { SITE_NAME } from '../constants/site';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || '/';
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(formData);
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      navigate(redirectTo, { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      if (err.response?.status === 401) {
        setError('\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef\uff0c\u8bf7\u91cd\u8bd5\u3002');
      } else if (err.response?.status === 400) {
        setError('\u8bf7\u68c0\u67e5\u60a8\u7684\u767b\u5f55\u4fe1\u606f\u540e\u518d\u8bd5\u3002');
      } else {
        setError('\u767b\u5f55\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrapper d-flex align-items-center justify-content-center min-vh-100">
      <div className="login-card shadow-lg p-4 rounded-4 bg-white">
        <div className="text-center mb-4">
          <div className="logo-placeholder mb-3">
            <i className="fas fa-paw fa-2x text-paw"></i>
          </div>
          <h3 className="fw-bold mt-2 text-paw">\u6b22\u8fce\u4f7f\u7528 {SITE_NAME}</h3>
          <p className="text-muted">\u767b\u5f55\u4ee5\u7ee7\u7eed\u60a8\u7684\u6551\u52a9\u4e4b\u65c5</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="username" className="form-label fw-semibold">\u7528\u6237\u540d</label>
            <input
              type="text"
              className="form-control form-control-lg rounded-3"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="\u8bf7\u8f93\u5165\u7528\u6237\u540d"
            />
          </div>

          <div className="mb-3">
            <label htmlFor="password" className="form-label fw-semibold">\u5bc6\u7801</label>
            <input
              type="password"
              className="form-control form-control-lg rounded-3"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="\u8bf7\u8f93\u5165\u5bc6\u7801"
            />
          </div>

          {error && (
            <div className="alert alert-danger rounded-3">{error}</div>
          )}

          <button
            type="submit"
            className="btn btn-paw w-100 py-2 rounded-3 fw-semibold"
            disabled={loading}
          >
            {loading ? '\u767b\u5f55\u4e2d...' : '\u767b\u5f55'}
          </button>
        </form>

        <div className="text-center mt-3">
          <p className="text-muted">
            <Link to="/forgot-password" className="text-decoration-none text-paw fw-semibold">
              \u5fd8\u8bb0\u5bc6\u7801\uff1f
            </Link>
          </p>
          <p className="text-muted">
            \u8fd8\u6ca1\u6709\u8d26\u53f7\uff1f{' '}
            <Link to="/register" className="text-decoration-none text-paw fw-semibold">
              \u7acb\u5373\u6ce8\u518c
            </Link>
          </p>
        </div>
      </div>

      <style>{`
        .login-wrapper {
          background: linear-gradient(to right, #fdf0e5, #fef5ef);
        }

        .login-card {
          max-width: 420px;
          width: 100%;
        }

        .btn-paw {
          background-color: #A0522D;
          border: none;
          color: white;
          transition: all 0.3s ease;
        }

        .btn-paw:hover {
          background-color: #8B4513;
        }

        .text-paw {
          color: #A0522D;
        }

        .form-control:focus {
          border-color: #A0522D;
          box-shadow: 0 0 0 0.2rem rgba(160, 82, 45, 0.25);
        }

        .logo-placeholder {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #A0522D, #8B4513);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto;
        }

        .logo-placeholder i {
          color: white;
        }

        @media (max-width: 576px) {
          .login-card {
            padding: 2rem 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default Login;
'''

AUTH_JS = r'''export const logout = (navigate) => {
  localStorage.removeItem('token');
  if (navigate) {
    navigate('/');
  } else {
    window.location.href = '/';
  }
};

export const confirmLogout = (navigate) => {
  if (window.confirm('\u786e\u5b9a\u8981\u9000\u51fa\u767b\u5f55\u5417\uff1f')) {
    logout(navigate);
  }
};
'''

FORGOT = r'''import React, { useState } from 'react';
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
      setMessage(`\u9a8c\u8bc1\u7801\u5df2\u53d1\u9001\u81f3\u6307\u5b9a\u90ae\u7bb1 ${RESET_CODE_MAILBOX}\uff0c\u8bf7\u67e5\u6536\u540e\u5728\u6b64\u8f93\u5165\u9a8c\u8bc1\u7801\u3002`);
      setStep(2);
    } catch (err) {
      const detail = err.response?.data?.email?.[0] || err.response?.data?.detail || '\u53d1\u9001\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u90ae\u7bb1\u662f\u5426\u6ce8\u518c\u6216\u7a0d\u540e\u91cd\u8bd5\u3002';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('\u4e24\u6b21\u8f93\u5165\u7684\u5bc6\u7801\u4e0d\u4e00\u81f4');
      return;
    }
    if (newPassword.length < 8) {
      setError('\u5bc6\u7801\u957f\u5ea6\u81f3\u5c11 8 \u4f4d');
      return;
    }
    setLoading(true);
    setError('');
    setMessage('');
    try {
      await authAPI.passwordResetConfirm({ email, code, new_password: newPassword });
      setMessage('\u5bc6\u7801\u91cd\u7f6e\u6210\u529f\uff0c\u5373\u5c06\u8df3\u8f6c\u81f3\u767b\u5f55\u9875...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const detail = err.response?.data?.non_field_errors?.[0]
        || err.response?.data?.detail
        || '\u91cd\u7f6e\u5931\u8d25\uff0c\u9a8c\u8bc1\u7801\u53ef\u80fd\u5df2\u8fc7\u671f\u3002';
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
          <h3 className="fw-bold">\u627e\u56de\u5bc6\u7801</h3>
          <p className="text-muted small">
            {step === 1
              ? '\u8f93\u5165\u6ce8\u518c\u90ae\u7bb1\u7533\u8bf7\u91cd\u7f6e\uff0c\u9a8c\u8bc1\u7801\u5c06\u53d1\u9001\u81f3\u6307\u5b9a\u90ae\u7bb1'
              : '\u8f93\u5165\u9a8c\u8bc1\u7801\u548c\u65b0\u5bc6\u7801'}
          </p>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}

        {step === 1 ? (
          <form onSubmit={handleRequestReset}>
            <div className="mb-3">
              <label htmlFor="email" className="form-label">\u90ae\u7bb1</label>
              <input
                type="email"
                id="email"
                className="form-control form-control-lg"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="\u8bf7\u8f93\u5165\u6ce8\u518c\u90ae\u7bb1"
              />
            </div>
            <button type="submit" className="btn btn-success w-100 py-2" disabled={loading}>
              {loading ? '\u53d1\u9001\u4e2d...' : '\u53d1\u9001\u9a8c\u8bc1\u7801'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirmReset}>
            <div className="mb-3">
              <label className="form-label">\u90ae\u7bb1</label>
              <input type="email" className="form-control" value={email} readOnly />
            </div>
            <div className="mb-3">
              <label htmlFor="code" className="form-label">\u9a8c\u8bc1\u7801</label>
              <input
                type="text"
                id="code"
                className="form-control"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                placeholder="6 \u4f4d\u9a8c\u8bc1\u7801"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="newPassword" className="form-label">\u65b0\u5bc6\u7801</label>
              <input
                type="password"
                id="newPassword"
                className="form-control"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                placeholder="\u81f3\u5c11 8 \u4f4d\u5b57\u7b26"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="confirmPassword" className="form-label">\u786e\u8ba4\u5bc6\u7801</label>
              <input
                type="password"
                id="confirmPassword"
                className="form-control"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                placeholder="\u518d\u6b21\u8f93\u5165\u65b0\u5bc6\u7801"
              />
            </div>
            <button type="submit" className="btn btn-success w-100 py-2 mb-2" disabled={loading}>
              {loading ? '\u91cd\u7f6e\u4e2d...' : '\u91cd\u7f6e\u5bc6\u7801'}
            </button>
            <button type="button" className="btn btn-outline-secondary w-100" onClick={() => setStep(1)}>
              \u91cd\u65b0\u53d1\u9001\u9a8c\u8bc1\u7801
            </button>
          </form>
        )}

        <div className="text-center mt-3">
          <Link to="/login" className="text-decoration-none text-success">\u8fd4\u56de\u767b\u5f55</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
'''


def decode_js(content: str) -> str:
    return content.encode('utf-8').decode('unicode_escape')


def write(rel_path: str, content: str) -> None:
    path = os.path.join(ROOT, rel_path.replace('/', os.sep))
    text = decode_js(content)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    # verify
    with open(path, 'r', encoding='utf-8') as f:
        sample = f.read()
    assert '\u7528\u6237\u540d' in sample or '\u9a8c\u8bc1\u7801' in sample or '\u786e\u5b9a' in sample
    print('OK', rel_path)


def main():
    write('pages/Login.js', LOGIN)
    write('utils/auth.js', AUTH_JS)
    write('pages/ForgotPassword.js', FORGOT)
    print('done')


if __name__ == '__main__':
    main()
