/**
 * @file MyPets.js
 * @module PawRescue
 * @description 页面组件：MyPets。
 */

import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { lostFoundAPI } from '../api/api';
import { LOST_FOUND_STATUS, LOST_FOUND_TYPE } from '../constants/site';
const MyPets = () => {
  const navigate = useNavigate();
  const [lostPosts, setLostPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
      return;
    }
    fetchMyData();
  }, [navigate]);
  const fetchMyData = async () => {
    try {
      setLoading(true);
      const res = await lostFoundAPI.getMyPosts();
      setLostPosts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setError('加载您的记录失败。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  const handleMarkFound = async (id) => {
    try {
      await lostFoundAPI.update(id, { status: 'found' });
      fetchMyData();
    } catch (err) {
      alert('操作失败');
    }
  };
  const handleCancel = async (id) => {
    if (!window.confirm('确定要撤销这条发布吗？')) return;
    try {
      await lostFoundAPI.update(id, { status: 'cancelled' });
      fetchMyData();
    } catch (err) {
      alert('操作失败');
    }
  };
  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
      </div>
    );
  }
  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }
  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0"><i className="fas fa-search me-2 text-danger"></i>我的报失</h2>
        <Link to="/lost-found/publish" className="btn btn-success">
          <i className="fas fa-plus me-1"></i>发布信息
        </Link>
      </div>
      {lostPosts.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <p>暂无报失寻主记录。</p>
          <Link to="/lost-found/publish" className="btn btn-outline-success">发布第一条信息</Link>
        </div>
      ) : (
        <div className="row">
          {lostPosts.map((post) => (
            <div key={post.id} className="col-md-6 mb-3">
              <div className="card h-100 shadow-sm">
                {post.photo_urls?.[0] && (
                  <img
                    src={post.photo_urls[0]}
                    className="card-img-top"
                    alt={post.pet_species}
                    style={{ height: '160px', objectFit: 'cover' }}
                  />
                )}
                <div className="card-body">
                  <div className="mb-2">
                    <span className={`badge ${post.post_type === 'lost' ? 'bg-danger' : 'bg-info'} me-1`}>
                      {LOST_FOUND_TYPE[post.post_type] || post.post_type}
                    </span>
                    <span className={`badge ${post.status === 'searching' ? 'bg-warning text-dark' : post.status === 'found' ? 'bg-success' : 'bg-secondary'}`}>
                      {LOST_FOUND_STATUS[post.status] || post.status}
                    </span>
                  </div>
                  <h5 className="card-title">{post.pet_species}</h5>
                  <p className="card-text text-muted small">{post.features?.slice(0, 80)}</p>
                  {post.address_text && (
                    <p className="small mb-2"><i className="fas fa-map-marker-alt me-1"></i>{post.address_text}</p>
                  )}
                  {Number(post.reward_amount) > 0 && (
                    <p className="small text-warning mb-2">
                      <i className="fas fa-coins me-1"></i>悬赏 {post.reward_amount} 元
                    </p>
                  )}
                  <div className="d-flex gap-2 mt-2">
                    <Link to={`/lost-found/${post.id}`} className="btn btn-outline-success btn-sm flex-grow-1">
                      查看详情
                    </Link>
                    {post.status === 'searching' && (
                      <>
                        <button
                          className="btn btn-outline-primary btn-sm"
                          onClick={() => handleMarkFound(post.id)}
                          title="标记已找回"
                        >
                          <i className="fas fa-check"></i> 已找回
                        </button>
                        <button
                          className="btn btn-outline-danger btn-sm"
                          onClick={() => handleCancel(post.id)}
                          title="撤销发布"
                        >
                          <i className="fas fa-times"></i> 撤销
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyPets;

