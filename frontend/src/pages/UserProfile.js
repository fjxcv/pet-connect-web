/**
 * @file UserProfile.js
 * @module PawRescue
 * @description 页面组件：UserProfile。
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, uploadAPI } from '../api/api';
const ROLE_LABELS = {
  admin: { label: '管理员', badge: 'bg-danger' },
  user: { label: '普通用户', badge: 'bg-success' },
  visitor: { label: '访客', badge: 'bg-secondary' },
};
const UserProfile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({
    email: '',
    nickname: '',
    phone: '',
    avatar_url: '',
    address: '',
  });
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchUserProfile();
  }, [navigate]);
  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const response = await authAPI.getProfile();
      const data = response.data;
      setUser(data);
      setForm({
        email: data.email || '',
        nickname: data.profile?.nickname || '',
        phone: data.profile?.phone || '',
        avatar_url: data.profile?.avatar_url || '',
        address: data.profile?.address || '',
      });
    } catch (err) {
      setError('加载个人资料失败，请稍后重试。');
      console.error('Error fetching user profile:', err);
    } finally {
      setLoading(false);
    }
  };
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };
  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setAvatarUploading(true);
      const response = await uploadAPI.upload(file, 'avatars');
      setForm((prev) => ({ ...prev, avatar_url: response.data.url }));
    } catch (err) {
      setError('头像上传失败，请重试。');
      console.error('Avatar upload error:', err);
    } finally {
      setAvatarUploading(false);
    }
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    setUpdateLoading(true);
    setUpdateSuccess(false);
    setError(null);
    try {
      await authAPI.updateProfile(form);
      setUpdateSuccess(true);
      setIsEditing(false);
      fetchUserProfile();
      setTimeout(() => setUpdateSuccess(false), 3000);
    } catch (err) {
      setError('更新资料失败，请重试。');
      console.error('Error updating profile:', err);
    } finally {
      setUpdateLoading(false);
    }
  };
  const getRoleDisplay = (role) => {
    const info = ROLE_LABELS[role] || { label: role || '未知', badge: 'bg-secondary' };
    return <span className={`badge ${info.badge}`}>{info.label}</span>;
  };
  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
        <p className="mt-2">正在加载个人资料...</p>
      </div>
    );
  }
  if (error && !user) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }
  const profile = user?.profile || {};
  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow-lg border-0">
            <div className="card-header bg-primary text-white text-center">
              <h3>
                <i className="fas fa-user-edit me-2"></i>
                个人资料
              </h3>
            </div>
            <div className="card-body p-4">
              {!isEditing ? (
                <div>
                  <div className="text-center mb-4">
                    {profile.avatar_url ? (
                      <img
                        src={profile.avatar_url}
                        alt="头像"
                        className="rounded-circle"
                        style={{ width: '80px', height: '80px', objectFit: 'cover' }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div
                        className="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center"
                        style={{ width: '80px', height: '80px' }}
                      >
                        <i className="fas fa-user fa-2x"></i>
                      </div>
                    )}
                  </div>
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label className="form-label fw-bold">用户名</label>
                      <p className="form-control-plaintext">{user.username}</p>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">邮箱</label>
                      <p className="form-control-plaintext">{user.email}</p>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">昵称</label>
                      <p className="form-control-plaintext">{profile.nickname || '未填写'}</p>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">手机号</label>
                      <p className="form-control-plaintext">{profile.phone || '未填写'}</p>
                    </div>
                    <div className="col-12">
                      <label className="form-label fw-bold">地址</label>
                      <p className="form-control-plaintext">{profile.address || '未填写'}</p>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">角色</label>
                      <p className="form-control-plaintext">{getRoleDisplay(profile.role)}</p>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">隐私政策同意</label>
                      <p className="form-control-plaintext">
                        {profile.has_privacy_consent ? (
                          <span className="badge bg-success">已同意</span>
                        ) : (
                          <span className="badge bg-warning text-dark">未同意</span>
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="d-grid gap-2 mt-4">
                    <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                      <i className="fas fa-edit me-2"></i>
                      编辑资料
                    </button>
                    <button className="btn btn-outline-secondary" onClick={() => navigate('/account')}>
                      <i className="fas fa-arrow-left me-2"></i>
                      返回个人中心
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label className="form-label fw-bold">邮箱</label>
                      <input
                        type="email"
                        className="form-control"
                        name="email"
                        value={form.email}
                        onChange={handleChange}
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">昵称</label>
                      <input
                        type="text"
                        className="form-control"
                        name="nickname"
                        value={form.nickname}
                        onChange={handleChange}
                        placeholder="显示名称"
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">手机号</label>
                      <input
                        type="tel"
                        className="form-control"
                        name="phone"
                        value={form.phone}
                        onChange={handleChange}
                        placeholder="联系电话"
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">地址</label>
                      <input
                        type="text"
                        className="form-control"
                        name="address"
                        value={form.address}
                        onChange={handleChange}
                        placeholder="您的地址"
                      />
                    </div>
                    <div className="col-12">
                      <label className="form-label fw-bold">头像</label>
                      <div className="d-flex gap-2 align-items-center">
                        <input
                          type="file"
                          className="form-control"
                          accept="image/*"
                          onChange={handleAvatarUpload}
                          disabled={avatarUploading}
                        />
                        {avatarUploading && (
                          <span className="spinner-border spinner-border-sm text-primary" role="status"></span>
                        )}
                      </div>
                      {form.avatar_url && (
                        <small className="text-muted d-block mt-1">当前：{form.avatar_url}</small>
                      )}
                    </div>
                  </div>
                  {updateSuccess && (
                    <div className="alert alert-success mt-3">
                      <i className="fas fa-check-circle me-2"></i>
                      资料更新成功！
                    </div>
                  )}
                  {error && (
                    <div className="alert alert-danger mt-3">
                      <i className="fas fa-exclamation-triangle me-2"></i>
                      {error}
                    </div>
                  )}
                  <div className="d-grid gap-2 mt-4">
                    <button type="submit" className="btn btn-primary" disabled={updateLoading}>
                      {updateLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          保存中...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-save me-2"></i>
                          保存修改
                        </>
                      )}
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline-secondary"
                      onClick={() => setIsEditing(false)}
                      disabled={updateLoading}
                    >
                      <i className="fas fa-times me-2"></i>
                      取消
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;

