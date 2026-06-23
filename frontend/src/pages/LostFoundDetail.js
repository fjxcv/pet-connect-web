import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { lostFoundAPI } from '../api/api';
import { LOST_FOUND_TYPE } from '../constants/site';

const LostFoundDetail = () => {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await lostFoundAPI.getById(id);
        setPost(response.data);
      } catch (err) {
        setError('加载详情失败，请稍后重试。');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPost();
  }, [id]);

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="text-center">
        <div className="alert alert-danger">{error || '未找到该信息'}</div>
        <Link to="/lost-found" className="btn btn-outline-secondary">返回列表</Link>
      </div>
    );
  }

  return (
    <div className="py-3">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/lost-found">报失寻主</Link></li>
          <li className="breadcrumb-item active">{post.pet_species}</li>
        </ol>
      </nav>

      <div className="card shadow-sm">
        <div className="card-body">
          <div className="mb-3">
            <span className={`badge ${post.post_type === 'lost' ? 'bg-danger' : 'bg-info'} me-2`}>
              {LOST_FOUND_TYPE[post.post_type] || post.post_type}
            </span>
            <span className="badge bg-secondary">{post.status}</span>
          </div>

          <h2 className="mb-3">{post.pet_species}</h2>

          {post.photo_urls?.length > 0 && (
            <div className="d-flex flex-wrap justify-content-center align-items-center gap-3 mb-4">
              {post.photo_urls.map((url, idx) => (
                <img
                  key={idx}
                  src={url}
                  alt={post.pet_species}
                  className="img-fluid rounded shadow-sm"
                  style={{ maxHeight: '360px', maxWidth: 'min(100%, 480px)', objectFit: 'contain' }}
                />
              ))}
            </div>
          )}

          <h5>体征特征</h5>
          <p style={{ whiteSpace: 'pre-wrap' }}>{post.features}</p>

          <hr />

          <div className="row">
            <div className="col-md-6 mb-3">
              <h6><i className="fas fa-map-marker-alt me-2 text-success"></i>位置</h6>
              <p className="mb-1">{post.address_text || '未填写地址'}</p>
              {post.latitude != null && post.longitude != null && (
                <a
                  href={`https://www.openstreetmap.org/?mlat=${post.latitude}&mlon=${post.longitude}#map=16/${post.latitude}/${post.longitude}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="small"
                >
                  在地图中查看
                </a>
              )}
            </div>
            {Number(post.reward_amount) > 0 && (
              <div className="col-md-6 mb-3">
                <h6><i className="fas fa-gift me-2 text-warning"></i>悬赏</h6>
                <p className="text-warning fw-bold">{post.reward_amount} 元</p>
              </div>
            )}
            {post.contact_phone && (
              <div className="col-md-6 mb-3">
                <h6><i className="fas fa-phone me-2"></i>联系电话</h6>
                <p>{post.contact_phone}</p>
              </div>
            )}
            {post.publisher && (
              <div className="col-md-6 mb-3">
                <h6><i className="fas fa-user me-2"></i>发布者</h6>
                <p>{post.publisher.username}</p>
              </div>
            )}
          </div>

          <small className="text-muted">
            发布时间：{new Date(post.created_at).toLocaleString()}
          </small>
        </div>
      </div>

      <div className="mt-4 text-center">
        <Link to="/lost-found" className="btn btn-outline-secondary">
          <i className="fas fa-arrow-left me-1"></i>返回列表
        </Link>
      </div>
    </div>
  );
};

export default LostFoundDetail;
