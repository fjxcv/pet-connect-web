/**
 * @file Login.js
 * @module PawRescue
 * @description 页面组件：Login。
 */

import { useState } from 'react';
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
        setError('用户名或密码错误，请重试。');
      } else if (err.response?.status === 400) {
        setError('请检查您的登录信息后再试。');
      } else {
        setError('登录失败，请稍后重试。');
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
          <h3 className="fw-bold mt-2 text-paw">欢迎使用 {SITE_NAME}</h3>
          <p className="text-muted">登录以继续您的救助之旅</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="username" className="form-label fw-semibold">用户名</label>
            <input
              type="text"
              className="form-control form-control-lg rounded-3"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="请输入用户名"
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label fw-semibold">密码</label>
            <input
              type="password"
              className="form-control form-control-lg rounded-3"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="请输入密码"
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
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
        <div className="text-center mt-3">
          <p className="text-muted">
            <Link to="/forgot-password" className="text-decoration-none text-paw fw-semibold">
              忘记密码？
            </Link>
          </p>
          <p className="text-muted">
            还没有账号？{' '}
            <Link to="/register" className="text-decoration-none text-paw fw-semibold">
              立即注册
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

