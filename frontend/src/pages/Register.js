<<<<<<< HEAD
import React, { useState, useEffect } from 'react';
=======
import React, { useState } from 'react';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/api';
import { SITE_NAME } from '../constants/site';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    has_privacy_consent: false,
  });
<<<<<<< HEAD
  const [code, setCode] = useState('');
  const [countdown, setCountdown] = useState(0);
  const [sendingCode, setSendingCode] = useState(false);
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const openPrivacyModal = () => setShowPrivacyModal(true);
  const closePrivacyModal = () => setShowPrivacyModal(false);

<<<<<<< HEAD
  useEffect(() => {
    if (countdown <= 0) return undefined;
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [countdown]);

  const requestCode = async () => {
    setError('');
    if (!formData.email) {
      setError('请先填写邮箱地址');
      return;
    }
    setError('');
    setSendingCode(true);
    try {
      await authAPI.requestRegisterCode({ email: formData.email });
      setCountdown(60);
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message;
      setError(detail || '发送验证码失败');
    } finally {
      setSendingCode(false);
    }
  };

=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.has_privacy_consent) {
      setError('注册前须同意隐私政策。');
      return;
    }

<<<<<<< HEAD
    if (!code.trim()) {
      setError('请输入验证码');
      return;
    }

=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    if (formData.password.length < 8) {
      setError('密码长度至少 8 位。');
      return;
    }

    setLoading(true);
    setError('');

    try {
<<<<<<< HEAD
      await authAPI.register({ ...formData, code });
=======
      await authAPI.register(formData);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      alert(`欢迎加入 ${SITE_NAME}！请登录。`);
      navigate('/login');
    } catch (err) {
      console.error('Registration error details:', err);

      if (err.response) {
        const status = err.response.status;
        const data = err.response.data;

<<<<<<< HEAD
        const extractMessage = (payload) => {
          if (!payload) return null;
          if (typeof payload === 'string') return payload;
          if (Array.isArray(payload)) return payload[0];
          if (payload.detail) return extractMessage(payload.detail);
          if (payload.non_field_errors) return extractMessage(payload.non_field_errors);
          const first = Object.values(payload)[0];
          return extractMessage(first);
        };

        const errorMessage = extractMessage(data);

        if (status === 400) {
          setError(errorMessage || '注册信息无效，请检查后重试。');
        } else if (status === 409) {
          setError(errorMessage || '该用户名已被占用，请换一个。');
        } else {
          setError(errorMessage || `注册失败（${status}），请稍后重试。`);
=======
        if (status === 400) {
          if (data.username) {
            setError(`用户名问题：${data.username[0]}`);
          } else if (data.email) {
            setError(`邮箱问题：${data.email[0]}`);
          } else if (data.password) {
            setError(`密码问题：${data.password[0]}`);
          } else if (data.has_privacy_consent) {
            setError(`隐私同意：${data.has_privacy_consent[0]}`);
          } else {
            setError('注册信息无效，请检查后重试。');
          }
        } else if (status === 409) {
          setError('该用户名已被占用，请换一个。');
        } else {
          setError(`注册失败（${status}），请稍后重试。`);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        }
      } else if (err.request) {
        setError('服务器无响应，请检查网络连接。');
      } else {
        setError('注册失败，请重试。');
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
          <h3 className="fw-bold mt-2 text-paw">欢迎加入 {SITE_NAME}</h3>
          <p className="text-muted">注册后即可参与社区救助与宠物分享。</p>
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
            <label htmlFor="email" className="form-label fw-semibold">邮箱地址</label>
            <input
              type="email"
              className="form-control form-control-lg rounded-3"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="请输入邮箱地址"
            />
          </div>

          <div className="mb-3">
<<<<<<< HEAD
            <label className="form-label fw-semibold">验证码</label>
            <div className="d-flex align-items-start gap-2">
              <input
                type="text"
                className="form-control form-control-lg rounded-3"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                placeholder="请输入验证码"
              />
              <button
                type="button"
                className="btn btn-code btn-lg"
                onClick={requestCode}
                disabled={sendingCode || countdown > 0}
              >
                {countdown > 0 ? `${countdown}s` : '获取验证码'}
              </button>
            </div>
          </div>

          <div className="mb-3">
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
            <label htmlFor="password" className="form-label fw-semibold">设置密码</label>
            <input
              type="password"
              className="form-control form-control-lg rounded-3"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              placeholder="至少 8 位字符"
            />
          </div>

          <div className="mb-3 form-check">
            <input
              type="checkbox"
              className="form-check-input"
              id="has_privacy_consent"
              name="has_privacy_consent"
              checked={formData.has_privacy_consent}
              onChange={handleChange}
              required
            />
            <label className="form-check-label privacy-text" htmlFor="has_privacy_consent">
              我已阅读并同意
              {' '}
              <button
                type="button"
                className="privacy-policy-link"
                onClick={openPrivacyModal}
              >
                隐私政策
              </button>
              {' '}及数据处理条款 *
            </label>
          </div>

          {error && (
            <div className="alert alert-danger rounded-3" role="alert">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-paw w-100 py-2 rounded-3 fw-semibold"
<<<<<<< HEAD
            disabled={loading || !formData.has_privacy_consent || !code.trim()}
=======
            disabled={loading || !formData.has_privacy_consent}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
          >
            {loading ? '注册中...' : '创建账号'}
          </button>
        </form>

        <div className="text-center mt-3">
          <p className="text-muted mb-0">
            已有账号？{' '}
            <Link to="/login" className="text-decoration-none text-paw fw-semibold">
              立即登录
            </Link>
          </p>
        </div>
      </div>

      {showPrivacyModal && (
        <div
          className="modal fade show d-block"
          tabIndex="-1"
          role="dialog"
          style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}
        >
          <div className="modal-dialog modal-dialog-centered" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">《隐私政策》</h5>
                <button type="button" className="btn-close" onClick={closePrivacyModal} aria-label="Close" />
              </div>
              <div className="modal-body">
                <p>
                  本平台严格保护用户个人隐私，本政策用于说明我们如何收集、使用、保存和保护您的个人信息。使用本站服务，即代表您同意本隐私政策全部内容。
                </p>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closePrivacyModal}>
                  关闭
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .login-wrapper {
          background: linear-gradient(to right, #fdf0e5, #fef5ef);
        }

        .login-card {
          max-width: 420px;
          width: 100%;
<<<<<<< HEAD
          padding: 2.5rem 2rem;
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        }

        .btn-paw {
          background-color: #A0522D;
          border: none;
          color: white;
          transition: all 0.3s ease;
        }

<<<<<<< HEAD
        .btn-paw:hover,
        .btn-paw:focus {
          background-color: #8B4513;
        }

        .btn-code {
          min-width: 140px;
          background-color: #fff5eb;
          border: 1px solid #d8a97f;
          color: #8b4513;
          font-weight: 600;
        }

        .btn-code:hover,
        .btn-code:focus {
          background-color: #ffe8d7;
          color: #6f3914;
        }

=======
        .btn-paw:hover {
          background-color: #8B4513;
        }

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        .text-paw {
          color: #A0522D;
        }

        .privacy-text {
          font-size: 13px;
          color: #9ca3af;
        }

        .privacy-policy-link {
          color: #A0522D;
          text-decoration: none;
          background: transparent;
          border: none;
          padding: 0;
          font: inherit;
          cursor: pointer;
        }

        .privacy-policy-link:hover {
          text-decoration: underline;
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

        /* 弹窗底部按钮居中核心样式 */
        .modal-footer {
          justify-content: center;
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

export default Register;
