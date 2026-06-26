/**
 * @file LostFoundList.js
 * @module PawRescue
 * @description 页面组件：LostFoundList。
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI, authAPI, lostFoundAPI } from '../api/api';
import AdminManageBar from '../components/AdminManageBar';
import ModerationReasonModal from '../components/ModerationReasonModal';
import { LOST_FOUND_STATUS, LOST_FOUND_TYPE } from '../constants/site';
const getApiError = (err) => {
  const d = err.response?.data;
  if (typeof d === 'string') return d;
  if (d?.detail) return String(d.detail);
  if (d?.reason) return String(d.reason);
  return err.message || '请求失败';
};
const POST_TYPE_TABS = [
  { key: '', label: '全部类型' },
  ...Object.entries(LOST_FOUND_TYPE).map(([key, label]) => ({ key, label })),
];
const STATUS_TABS = [
  { key: '', label: '全部状态' },
  ...Object.entries(LOST_FOUND_STATUS).map(([key, label]) => ({ key, label })),
];
const LostFoundList = () => {
  const [posts, setPosts] = useState([]);
  const [postType, setPostType] = useState('');
  const [status, setStatus] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [searchQ, setSearchQ] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // 附近搜索
  const [nearbyMode, setNearbyMode] = useState(false);
  const [nearbyLoading, setNearbyLoading] = useState(false);
  const [nearbyError, setNearbyError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [nearbyRadius, setNearbyRadius] = useState(5);
  const [nearbyLocationFixed, setNearbyLocationFixed] = useState(null); // 固定用户位置，避免重复定位
  // 悬赏筛
  const [hasReward, setHasReward] = useState(false);
  // 地图显示
  const [showMap, setShowMap] = useState(false);
  // 当前用户ID（用于显示管理按钮）
  const [currentUserId, setCurrentUserId] = useState(null);
  const [modal, setModal] = useState(null);
  const [modalSubmitting, setModalSubmitting] = useState(false);
  useEffect(() => {
    authAPI.getProfile().then((res) => {
      setCurrentUserId(res.data?.id || null);
    }).catch(() => {});
  }, []);
  useEffect(() => {
    const timer = setTimeout(() => setSearchQ(searchInput.trim()), 300);
    return () => clearTimeout(timer);
  }, [searchInput]);
  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (postType) params.post_type = postType;
      if (status) params.status = status;
      if (searchQ) params.q = searchQ;
      if (hasReward) params.has_reward = 'true';
      const response = await lostFoundAPI.getAll(params);
      setPosts(Array.isArray(response.data) ? response.data : response.data?.results ?? []);
    } catch (err) {
      setError('加载信息失败，请稍后重试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [postType, status, searchQ, hasReward]);
  useEffect(() => {
    if (!nearbyMode) {
      fetchPosts();
    }
  }, [fetchPosts, nearbyMode]);
  // 执行附近搜索（使用已保存的位置）
  const doNearbySearch = useCallback(async (location, radius, type, st, q, reward) => {
    if (!location) return;
    setNearbyLoading(true);
    setNearbyError(null);
    try {
      const params = {
        lat: location.lat,
        lon: location.lon,
        radius: radius,
      };
      if (type) params.post_type = type;
      if (st) params.status = st;
      if (q) params.q = q;
      if (reward) params.has_reward = 'true';
      const res = await lostFoundAPI.getNearby(params);
      setPosts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setNearbyError('附近搜索失败，请稍后重试');
      console.error(err);
    } finally {
      setNearbyLoading(false);
    }
  }, []);
  // 附近模式下，筛选条件变化时自动重新搜索
  useEffect(() => {
    if (nearbyMode && nearbyLocationFixed) {
      doNearbySearch(nearbyLocationFixed, nearbyRadius, postType, status, searchQ, hasReward);
    }
  }, [nearbyMode, nearbyLocationFixed, nearbyRadius, postType, status, searchQ, hasReward, doNearbySearch]);
  const refreshPosts = useCallback(() => {
    if (nearbyMode && nearbyLocationFixed) {
      doNearbySearch(nearbyLocationFixed, nearbyRadius, postType, status, searchQ, hasReward);
    } else {
      fetchPosts();
    }
  }, [nearbyMode, nearbyLocationFixed, nearbyRadius, postType, status, searchQ, hasReward, doNearbySearch, fetchPosts]);
  const openModerationModal = (type, post) => {
    if (type === 'delete') {
      setModal({
        type: 'delete',
        post,
        title: '删除报失/寻主信息',
        actionLabel: '确认删除',
        targetLabel: `${post.pet_species} - ${post.address_text || post.id}`,
      });
    } else {
      setModal({
        type: 'ban',
        post,
        title: '封禁用户',
        actionLabel: '确认封禁',
        targetLabel: post.publisher?.username || `用户 #${post.publisher?.id}`,
      });
    }
  };
  const handleModerationConfirm = async (reason) => {
    if (!modal) return;
    setModalSubmitting(true);
    try {
      if (modal.type === 'delete') {
        await adminAPI.createModeration({
          content_type: 'lost_found_post',
          content_id: modal.post.id,
          action: 'delete',
          reason,
          target_summary: `${modal.post.pet_species}`.slice(0, 200),
        });
      } else {
        await adminAPI.createModeration({
          content_type: 'user',
          content_id: modal.post.publisher.id,
          action: 'ban',
          reason,
          target_summary: modal.post.publisher?.username || '',
        });
      }
      setModal(null);
      alert(modal.type === 'delete' ? '信息已删除' : '用户已封禁');
      refreshPosts();
    } catch (err) {
      alert(getApiError(err));
    } finally {
      setModalSubmitting(false);
    }
  };
  // 首次附近搜索（获取位置）
  const handleNearbySearch = () => {
    if (!navigator.geolocation) {
      setNearbyError('您的浏览器不支持地理位置功能');
      return;
    }
    setNearbyLoading(true);
    setNearbyError(null);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        const loc = { lat: latitude, lon: longitude };
        setUserLocation(loc);
        setNearbyLocationFixed(loc);
        setNearbyMode(true);
        setShowMap(true);
        // doNearbySearch 会由上面的 useEffect 自动触发
      },
      (err) => {
        let msg = '获取位置失败';
        if (err.code === 1) msg = '请允许定位权限以使用附近搜索';
        else if (err.code === 2) msg = '位置信息不可用';
        else if (err.code === 3) msg = '获取位置超时';
        setNearbyError(msg);
        setNearbyLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };
  // 逢出附近搜索模弄
  const exitNearbyMode = () => {
    setNearbyMode(false);
    setShowMap(false);
    setUserLocation(null);
    setNearbyLocationFixed(null);
    setNearbyError(null);
  };
  // 使用 Leaflet 构建带多个标记点的地图 HTML
  const mapHtml = useMemo(() => {
    if (!userLocation) return '';
    const allPoints = [{ lat: userLocation.lat, lon: userLocation.lon }];
    posts
      .filter((p) => p.latitude && p.longitude)
      .forEach((p) => allPoints.push({ lat: parseFloat(p.latitude), lon: parseFloat(p.longitude) }));
    const lats = allPoints.map((pt) => pt.lat);
    const lons = allPoints.map((pt) => pt.lon);
    const minLat = Math.min(...lats) - 0.01;
    const maxLat = Math.max(...lats) + 0.01;
    const minLon = Math.min(...lons) - 0.01;
    const maxLon = Math.max(...lons) + 0.01;
    const centerLat = (minLat + maxLat) / 2;
    const centerLon = (minLon + maxLon) / 2;
    // 构建标记点 JS 代码
    const markersJs = [];
    // 用户位置（腾讯地图风格定位图标 - 蓝色水滴形）
    markersJs.push(`L.marker([${userLocation.lat}, ${userLocation.lon}], {icon: L.divIcon({className: 'user-marker', html: '<div style="position:relative;width:28px;height:40px"><svg width="28" height="40" viewBox="0 0 28 40" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 26 14 26s14-15.5 14-26C28 6.268 21.732 0 14 0z" fill="#4A90D9"/><circle cx="14" cy="14" r="6" fill="white"/></svg></div>', iconSize: [28,40], iconAnchor: [14,40]})}).addTo(map).bindPopup('我的位置')`);
    // 帖子标记（点击跳转到详情页）
    posts
      .filter((p) => p.latitude && p.longitude)
      .forEach((p) => {
        const color = p.post_type === 'lost' ? '#ef4444' : '#3b82f6';
        const species = (p.pet_species || '').replace(/'/g, "\\'");
        markersJs.push(`L.marker([${p.latitude}, ${p.longitude}], {icon: L.divIcon({className: 'post-marker', html: '<a href="/lost-found/${p.id}" target="_parent" style="display:block;width:16px;height:16px;border-radius:50%;background:${color};border:3px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);cursor:pointer" title="${species}"></a>', iconSize: [16,16], iconAnchor: [8,8]})}).addTo(map)`);
      });
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    * { margin: 0; padding: 0; }
    html, body, #map { width: 100%; height: 100%; }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    var map = L.map('map').setView([${centerLat}, ${centerLon}], 13);
    L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
      maxZoom: 19,
      subdomains: ['1', '2', '3', '4'],
      attribution: '© 高德地图'
    }).addTo(map);
    ${markersJs.join(';\n    ')}
    // 自动适配边界
    var bounds = L.latLngBounds([${minLat}, ${minLon}], [${maxLat}, ${maxLon}]);
    map.fitBounds(bounds, {padding: [30, 30]});
  </script>
</body>
</html>`;
  }, [userLocation, posts]);
  return (
    <div className="py-3">
      <ModerationReasonModal
        show={!!modal}
        title={modal?.title}
        targetLabel={modal?.targetLabel}
        actionLabel={modal?.actionLabel}
        submitting={modalSubmitting}
        onConfirm={handleModerationConfirm}
        onCancel={() => !modalSubmitting && setModal(null)}
      />
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
        <h2><i className="fas fa-search-location me-2 text-success"></i>报失寻主</h2>
        <div className="d-flex gap-2">
          {nearbyMode ? (
            <button type="button" className="btn btn-outline-secondary" onClick={exitNearbyMode}>
              <i className="fas fa-list me-1"></i>返回列表
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-outline-info"
              onClick={handleNearbySearch}
              disabled={nearbyLoading}
            >
              <i className="fas fa-map-marker-alt me-1"></i>
              {nearbyLoading ? '定位中...' : '附近搜索'}
            </button>
          )}
          <Link to="/lost-found/publish" className="btn btn-success">
            <i className="fas fa-plus me-1"></i>发布信息
          </Link>
        </div>
      </div>
      {/* 附近搜索控制栏 */}
      {nearbyMode && (
        <div className="alert alert-info d-flex flex-wrap align-items-center gap-2 mb-3">
          <i className="fas fa-map-marked-alt"></i>
          <span className="fw-medium">附近搜索模式</span>
          <span className="text-muted small">
            {userLocation ? `当前位置已获取` : '正在获取位置...'}
          </span>
          <div className="ms-auto d-flex align-items-center gap-2">
            <label className="small text-muted">搜索范围：</label>
            <select
              className="form-select form-select-sm"
              style={{ width: 'auto' }}
              value={nearbyRadius}
              onChange={(e) => setNearbyRadius(Number(e.target.value))}
            >
              <option value={1}>1 公里</option>
              <option value={3}>3 公里</option>
              <option value={5}>5 公里</option>
              <option value={10}>10 公里</option>
              <option value={20}>20 公里</option>
            </select>
            <button
              type="button"
              className="btn btn-sm btn-outline-info"
              onClick={handleNearbySearch}
              disabled={nearbyLoading}
            >
              <i className="fas fa-redo me-1"></i>重新搜索
            </button>
          </div>
        </div>
      )}
      {nearbyError && (
        <div className="alert alert-warning alert-dismissible fade show">
          {nearbyError}
          <button type="button" className="btn-close" onClick={() => setNearbyError(null)}></button>
        </div>
      )}
      {/* 地图 */}
      {showMap && userLocation && (
        <div className="mb-4">
          <div className="card shadow-sm">
            <div className="card-header d-flex justify-content-between align-items-center">
              <span><i className="fas fa-map me-1"></i>附近位置</span>
              <button
                type="button"
                className="btn btn-sm btn-outline-secondary"
                onClick={() => setShowMap(!showMap)}
              >
                {showMap ? '收起地图' : '展开地图'}
              </button>
            </div>
            {showMap && (
              <div className="card-body p-0">
                <iframe
                  title="附近地图"
                  srcDoc={mapHtml}
                  width="100%"
                  height="350"
                  style={{ border: 0 }}
                  allowFullScreen
                  loading="lazy"
                ></iframe>
                <div className="p-2 small text-muted d-flex align-items-center gap-3 flex-wrap">
                  <span><span className="badge bg-danger me-1" style={{width:12,height:12,borderRadius:'50%',display:'inline-block',padding:0}}>&nbsp;</span>寻宠</span>
                  <span><span className="badge bg-info me-1" style={{width:12,height:12,borderRadius:'50%',display:'inline-block',padding:0}}>&nbsp;</span>招领</span>
                  <span><svg width="14" height="20" viewBox="0 0 28 40" style={{verticalAlign:'middle',marginRight:4}}><path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 26 14 26s14-15.5 14-26C28 6.268 21.732 0 14 0z" fill="#4A90D9"/><circle cx="14" cy="14" r="6" fill="white"/></svg>你的位置</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {/* 搜索和筛选 */}
      <div className="row mb-3">
        <div className="col-md-6">
          <div className="input-group">
            <span className="input-group-text"><i className="fas fa-search" /></span>
            <input
              type="search"
              className="form-control"
              placeholder="搜索物种、特征、地址..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </div>
        </div>
        <div className="col-md-3 d-flex align-items-center">
          <div className="form-check">
            <input
              type="checkbox"
              className="form-check-input"
              id="hasReward"
              checked={hasReward}
              onChange={(e) => setHasReward(e.target.checked)}
            />
            <label className="form-check-label" htmlFor="hasReward">
              <i className="fas fa-coins text-warning me-1"></i>仅看有赏金
            </label>
          </div>
        </div>
      </div>
      <ul className="nav nav-pills mb-2 flex-wrap gap-1">
        {POST_TYPE_TABS.map((tab) => (
          <li className="nav-item" key={`type-${tab.key || 'all'}`}>
            <button
              type="button"
              className={`nav-link ${postType === tab.key ? 'active' : ''}`}
              onClick={() => setPostType(tab.key)}
            >
              {tab.label}
            </button>
          </li>
        ))}
      </ul>
      <ul className="nav nav-pills mb-4 flex-wrap gap-1">
        {STATUS_TABS.map((tab) => (
          <li className="nav-item" key={`status-${tab.key || 'all'}`}>
            <button
              type="button"
              className={`nav-link ${status === tab.key ? 'active' : ''}`}
              onClick={() => setStatus(tab.key)}
            >
              {tab.label}
            </button>
          </li>
        ))}
      </ul>
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-success" role="status">
            <span className="visually-hidden">加载中...</span>
          </div>
        </div>
      )}
      {error && <div className="alert alert-danger">{error}</div>}
      {!loading && !error && (
        <div className="row">
          {posts.length === 0 ? (
            <div className="col-12 text-center text-muted py-5">
              {nearbyMode ? '附近暂无信息' : '暂无信息'}
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="col-md-6 col-lg-4 mb-4">
                <div className="card h-100 shadow-sm">
                  {post.photo_urls?.[0] && (
                    <img
                      src={post.photo_urls[0]}
                      className="card-img-top"
                      alt={post.pet_species}
                      style={{ height: '180px', objectFit: 'cover' }}
                    />
                  )}
                  <div className="card-body text-start">
                    <AdminManageBar
                      userId={post.publisher?.id}
                      onDelete={() => openModerationModal('delete', post)}
                      onBanUser={post.publisher?.id ? () => openModerationModal('ban', post) : undefined}
                    />
                    <div className="mb-2">
                      <span className={`badge ${post.post_type === 'lost' ? 'bg-danger' : 'bg-info'}`}>
                        {LOST_FOUND_TYPE[post.post_type] || post.post_type}
                      </span>
                      <span className="badge bg-secondary ms-1">
                        {LOST_FOUND_STATUS[post.status] || post.status}
                      </span>
                      {post.distance_km !== undefined && (
                        <span className="badge bg-warning text-dark ms-1">
                          {post.distance_km} km
                        </span>
                      )}
                    </div>
                    <h5 className="card-title text-start">{post.pet_species}</h5>
                    <p className="card-text text-muted small text-start">{post.features?.slice(0, 80)}</p>
                    {post.address_text && (
                      <p className="small mb-2 text-start"><i className="fas fa-map-marker-alt me-1"></i>{post.address_text}</p>
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
                      {currentUserId && post.publisher?.id === currentUserId && post.status === 'searching' && (
                        <>
                          <button
                            className="btn btn-outline-primary btn-sm"
                            onClick={async () => {
                              await lostFoundAPI.update(post.id, { status: 'found' });
                              fetchPosts();
                            }}
                            title="标记已找到"
                          >
                            <i className="fas fa-check"></i>
                          </button>
                          <button
                            className="btn btn-outline-danger btn-sm"
                            onClick={async () => {
                              if (!window.confirm('确定要撤销这条发布吗？')) return;
                              await lostFoundAPI.update(post.id, { status: 'cancelled' });
                              fetchPosts();
                            }}
                            title="撤销发布"
                          >
                            <i className="fas fa-times"></i>
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default LostFoundList;

