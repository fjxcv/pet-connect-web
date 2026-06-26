/**
 * @file LostFoundPublish.js
 * @module PawRescue
 * @description 页面组件：LostFoundPublish。
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { aiAPI, lostFoundAPI, uploadAPI } from '../api/api';
import { LOST_FOUND_TYPE } from '../constants/site';
import { AMAP_KEY, AMAP_TILE_URL, AMAP_TILE_OPTIONS } from '../config/amap';
import { formatApiError, roundCoordinate } from '../utils/apiError';
/**
 * GCJ-02 转 WGS-84（火星坐标系 → GPS 标准坐标系）
 * 高德地图使用 GCJ-02，Leaflet/OpenStreetMap 使用 WGS-84
 * 如果不转换，高德搜索到的坐标在 Leaflet 地图上会有几百米偏移
 */
function gcj02ToWgs84(lat, lng) {
  const a = 6378245.0; // 长半轴
  const ee = 0.00669342162296594323; // 扁率
  function transformLat(x, y) {
    let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
    ret += ((20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0) / 3.0;
    ret += ((20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin((y / 3.0) * Math.PI)) * 2.0) / 3.0;
    ret += ((160.0 * Math.sin((y / 12.0) * Math.PI) + 320.0 * Math.sin((y * Math.PI) / 30.0)) * 2.0) / 3.0;
    return ret;
  }
  function transformLng(x, y) {
    let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
    ret += ((20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0) / 3.0;
    ret += ((20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin((x / 3.0) * Math.PI)) * 2.0) / 3.0;
    ret += ((150.0 * Math.sin((x / 12.0) * Math.PI) + 300.0 * Math.sin((x / 30.0) * Math.PI)) * 2.0) / 3.0;
    return ret;
  }
  // 判断是否在中国境内，不在则不转换
  if (lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271) {
    return { lat, lng };
  }
  let dLat = transformLat(lng - 105.0, lat - 35.0);
  let dLng = transformLng(lng - 105.0, lat - 35.0);
  const radLat = (lat / 180.0) * Math.PI;
  let magic = Math.sin(radLat);
  magic = 1 - ee * magic * magic;
  const sqrtMagic = Math.sqrt(magic);
  dLat = (dLat * 180.0) / (((a * (1 - ee)) / (magic * sqrtMagic)) * Math.PI);
  dLng = (dLng * 180.0) / ((a / sqrtMagic) * Math.cos(radLat) * Math.PI);
  return {
    lat: lat - dLat,
    lng: lng - dLng,
  };
}
/**
 * 高德地图 POI 关键词搜索
 * https://restapi.amap.com/v3/place/text
 */
async function amapPlaceText(keywords, city = '成都') {
  if (!keywords.trim()) return [];
  const url =
    `https://restapi.amap.com/v3/place/text?key=${AMAP_KEY}` +
    `&keywords=${encodeURIComponent(keywords)}` +
    `&types=&city=${encodeURIComponent(city)}` +
    `&offset=10&page=1&extensions=base`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.status !== '1' || !Array.isArray(data.pois)) {
    console.warn('高德 place/text 返回异常:', data);
    return [];
  }
  return data.pois.map((poi) => {
    const gcjLat = parseFloat(poi.location.split(',')[1]);
    const gcjLng = parseFloat(poi.location.split(',')[0]);
    return {
      id: poi.id,
      name: poi.name,
      address: poi.address || '',
      lat: gcjLat,
      lng: gcjLng,
      distance: poi.distance,
    };
  });
}
/**
 * 高德地图逆地理编码（坐标 → 文字地址）
 * 注意：传入的坐标需要是 GCJ-02 坐标系
 * 因为 Leaflet 地图用的是 WGS-84，所以需要先转成 GCJ-02 再请求高德 API
 * https://restapi.amap.com/v3/geocode/regeo
 */
async function amapRegeo(lat, lng) {
  // 将 WGS-84 转回 GCJ-02 再请求高德 API
  // 简单近似：直接用 WGS-84 坐标请求高德逆地理编码，高德会自动处理
  const location = `${lng},${lat}`;
  const url =
    `https://restapi.amap.com/v3/geocode/regeo?key=${AMAP_KEY}` +
    `&location=${encodeURIComponent(location)}` +
    `&radius=1000&extensions=base`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.status !== '1' || !data.regeocode) {
    console.warn('高德 regeo 返回异常:', data);
    return '';
  }
  return data.regeocode.formatted_address || '';
}
const LostFoundPublish = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    post_type: 'lost',
    pet_species: '',
    features: '',
    latitude: '',
    longitude: '',
    address_text: '',
    reward_amount: '0',
    contact_phone: '',
  });
  const [photoUrls, setPhotoUrls] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [locating, setLocating] = useState(false);
  const [locationHint, setLocationHint] = useState('');
  const [error, setError] = useState('');
  const [photoError, setPhotoError] = useState('');
  const [mapReady, setMapReady] = useState(false);
  const mapCenter = useMemo(() => [30.5728, 104.0668], []); // 默认成都
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const leafletMapRef = useRef(null);
  // ---- 地点搜索（高德 POI）----
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchTimerRef = useRef(null);
  const dropdownRef = useRef(null);
  // 防抖搜索
  const handleSearchInput = (e) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    if (!val.trim()) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }
    searchTimerRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const results = await amapPlaceText(val);
        setSearchResults(results);
        setShowDropdown(results.length > 0);
      } catch (err) {
        console.error('地点搜索失败:', err);
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 400);
  };
  // 选中搜索结果
  const handleSelectResult = (poi) => {
    setSearchQuery(poi.name);
    setShowDropdown(false);
    // 更新表单
    setForm((f) => ({
      ...f,
      latitude: String(roundCoordinate(poi.lat)),
      longitude: String(roundCoordinate(poi.lng)),
      address_text: poi.address ? `${poi.name}, ${poi.address}` : poi.name,
    }));
    setLocationHint(`已定位到：${poi.name}`);
    // 移动地图标记
    if (leafletMapRef.current && markerRef.current) {
      leafletMapRef.current.setView([poi.lat, poi.lng], 16);
      markerRef.current.setLatLng([poi.lat, poi.lng]);
    }
  };
  // 点击外部关闭下拉
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  const hasCoordinates = () => {
    const lat = parseFloat(form.latitude);
    const lng = parseFloat(form.longitude);
    return Number.isFinite(lat) && Number.isFinite(lng);
  };
  // 逆地理编码（高德）：坐标 → 文字地址
  const reverseGeocode = useCallback(async (lat, lng) => {
    try {
      const addr = await amapRegeo(lat, lng);
      return addr;
    } catch {
      return '';
    }
  }, []);
  // 更新地图标记位置
  const updateMarkerPosition = useCallback(async (lat, lng) => {
    const roundedLat = roundCoordinate(lat);
    const roundedLng = roundCoordinate(lng);
    setForm((f) => ({
      ...f,
      latitude: String(roundedLat),
      longitude: String(roundedLng),
    }));
    // 高德逆地理编码获取地址
    const addr = await reverseGeocode(roundedLat, roundedLng);
    if (addr) {
      setForm((f) => ({ ...f, address_text: addr }));
      setSearchQuery(addr);
    }
    setLocationHint(`已定位：${roundedLat}, ${roundedLng}`);
  }, [reverseGeocode]);
  // 初始化地图
  useEffect(() => {
    if (!mapRef.current || leafletMapRef.current) return;
    let cancelled = false;
    const initMap = () => {
      if (cancelled || !mapRef.current) return;
      const L = window.L;
      const map = L.map(mapRef.current).setView(mapCenter, 13);
      L.tileLayer(AMAP_TILE_URL, AMAP_TILE_OPTIONS).addTo(map);
      const marker = L.marker(mapCenter, { draggable: true }).addTo(map);
      markerRef.current = marker;
      leafletMapRef.current = map;
      // 点击地图移动标记
      map.on('click', (e) => {
        marker.setLatLng(e.latlng);
        updateMarkerPosition(e.latlng.lat, e.latlng.lng);
      });
      // 拖动标记
      marker.on('dragend', () => {
        const pos = marker.getLatLng();
        updateMarkerPosition(pos.lat, pos.lng);
      });
      if (!cancelled) setMapReady(true);
    };
    if (window.L) {
      initMap();
    } else {
      if (!document.querySelector('link[href*="leaflet.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }
      if (!document.querySelector('script[src*="leaflet.js"]')) {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = initMap;
        script.onerror = () => { if (!cancelled) setError('地图加载失败，请刷新页面重试'); };
        document.body.appendChild(script);
      } else {
        const check = setInterval(() => {
          if (window.L) {
            clearInterval(check);
            initMap();
          }
        }, 200);
      }
    }
    return () => {
      cancelled = true;
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
        markerRef.current = null;
        setMapReady(false);
      }
    };
  }, [mapCenter, updateMarkerPosition]);
  // 当使用当前位置时，移动地图和标记
  useEffect(() => {
    if (mapReady && hasCoordinates() && leafletMapRef.current && markerRef.current) {
      const lat = parseFloat(form.latitude);
      const lng = parseFloat(form.longitude);
      if (Number.isFinite(lat) && Number.isFinite(lng)) {
        leafletMapRef.current.setView([lat, lng], 15);
        markerRef.current.setLatLng([lat, lng]);
      }
    }
  }, [form.latitude, form.longitude, mapReady]);
  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('当前浏览器不支持定位，请换用手机浏览器或 Chrome/Edge。');
      return;
    }
    setError('');
    setLocating(true);
    setLocationHint('');
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = roundCoordinate(pos.coords.latitude);
        const lng = roundCoordinate(pos.coords.longitude);
        setForm((f) => ({
          ...f,
          latitude: String(lat),
          longitude: String(lng),
        }));
        // 高德逆地理编码
        const addr = await reverseGeocode(lat, lng);
        if (addr) {
          setForm((f) => ({ ...f, address_text: addr }));
          setSearchQuery(addr);
        }
        const meters = Math.round(pos.coords.accuracy);
        setLocationHint(`已记录当前位置（定位精度约 ${meters} 米）`);
        setLocating(false);
      },
      (geoErr) => {
        setLocating(false);
        const hints = {
          1: '您拒绝了位置权限，请在浏览器设置中允许定位后重试。',
          2: '暂时无法获取位置，请稍后重试或检查系统定位是否开启。',
          3: '定位超时，请到开阔处重试。',
        };
        setError(hints[geoErr.code] || '获取位置失败，请检查浏览器定位权限。');
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 120000 },
    );
  };
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };
  const handlePhotoUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    setUploading(true);
    setError('');
    try {
      const uploaded = [];
      for (const file of files) {
        const res = await uploadAPI.upload(file, 'lost-found');
        uploaded.push(res.data.url);
      }
      setPhotoUrls((prev) => [...prev, ...uploaded]);
    } catch (err) {
      setError('图片上传失败，请重试。');
      console.error(err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };
  const removePhoto = (index) => {
    setPhotoUrls((prev) => prev.filter((_, i) => i !== index));
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    const address = form.address_text.trim();
    if (!address) {
      setError('请填写事发地点或附近地标。');
      return;
    }
    if (!photoUrls.length) {
      setPhotoError('请至少上传 1 张宠物照片。');
      return;
    }
    setPhotoError('');
    setSubmitting(true);
    setError('');
    try {
      const lat = roundCoordinate(form.latitude);
      const lng = roundCoordinate(form.longitude);
      const payload = {
        post_type: form.post_type,
        pet_species: form.pet_species,
        features: form.features,
        address_text: address,
        reward_amount: parseFloat(form.reward_amount) || 0,
        contact_phone: form.contact_phone || null,
        photo_urls: photoUrls,
      };
      if (lat != null && lng != null) {
        payload.latitude = lat;
        payload.longitude = lng;
      }
      const res = await lostFoundAPI.create(payload);
      navigate(`/lost-found/${res.data.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        detail === 'account_banned'
          ? '账号已被封禁，无法发布信息。'
          : formatApiError(err, '发布失败，请检查表单后重试。')
      );
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <div className="py-3">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/lost-found">报失寻主</Link></li>
          <li className="breadcrumb-item active">发布信息</li>
        </ol>
      </nav>
      <h2 className="mb-4"><i className="fas fa-edit me-2 text-success"></i>发布报失/寻主信息</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit} className="card shadow-sm">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-12">
              <label className="form-label d-block">类型 <span className="text-danger">*</span></label>
              <div className="btn-group w-100 flex-wrap" role="group">
                {Object.entries(LOST_FOUND_TYPE).map(([key, label]) => (
                  <button
                    key={key}
                    type="button"
                    className={`btn flex-fill ${form.post_type === key ? 'btn-success' : 'btn-outline-secondary'}`}
                    onClick={() => setForm((f) => ({ ...f, post_type: key }))}
                  >
                    {label}
                    <small className="d-block opacity-75">{key === 'lost' ? '宠物走失' : '发现流浪/招领'}</small>
                  </button>
                ))}
              </div>
            </div>
            <div className="col-md-6">
              <label className="form-label">宠物种类</label>
              <input type="text" name="pet_species" className="form-control" value={form.pet_species} onChange={handleChange} required placeholder="如：中华田园猫" />
            </div>
            <div className="col-12">
              <label className="form-label">特征描述</label>
              <button type="button" className="btn btn-outline-success btn-sm mb-2" onClick={async () => {
                if (!photoUrls[0]) { alert('请先上传照片'); return; }
                try {
                  const res = await aiAPI.breedDetect({
                    image_url: photoUrls[0],
                    description: `${form.pet_species} ${form.features}`,
                  });
                  const parts = [
                    res.data.species && `物种：${res.data.species}`,
                    res.data.breed && `品种：${res.data.breed}`,
                    res.data.summary && res.data.summary !== '不确定' && `特征：${res.data.summary}`,
                  ].filter(Boolean);
                  setForm((f) => ({ ...f, features: parts.join('；') || res.data.result || f.features }));
                } catch (err) { alert(err.response?.data?.detail || 'AI 失败'); }
              }}>AI 识图辅助特征</button>
              <textarea name="features" className="form-control" rows={4} value={form.features} onChange={handleChange} required placeholder="毛色、体型、特殊标志等" />
            </div>
            {/* ========== 事发地点（地图选点 + 高德搜索） ========== */}
            <div className="col-12">
              <label className="form-label">
                事发地点 <small className="text-muted">（搜索地点，或在地图上点击/拖动标记精确定位）</small>
              </label>
              {/* 搜索框 + 操作按钮 */}
              <div className="mb-2 position-relative" ref={dropdownRef}>
                <div className="d-flex flex-wrap align-items-center gap-2">
                  <div className="position-relative flex-grow-1" style={{ maxWidth: 500 }}>
                    <input
                      type="text"
                      className="form-control form-control-sm"
                      placeholder="搜索地点名称（如：春熙路、天府广场）"
                      value={searchQuery}
                      onChange={handleSearchInput}
                      onFocus={() => { if (searchResults.length > 0) setShowDropdown(true); }}
                    />
                    {searching && (
                      <span className="position-absolute end-0 top-50 translate-middle-y me-2">
                        <span className="spinner-border spinner-border-sm" role="status" />
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    className="btn btn-outline-success btn-sm"
                    onClick={handleUseCurrentLocation}
                    disabled={locating || submitting}
                  >
                    {locating ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
                        定位中...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-location-arrow me-1" />
                        定位到我
                      </>
                    )}
                  </button>
                  {hasCoordinates() && (
                    <span className="badge bg-light text-success border">已定位</span>
                  )}
                </div>
                {/* 搜索下拉结果 */}
                {showDropdown && (
                  <ul
                    className="list-group position-absolute top-100 start-0 w-100 shadow-sm"
                    style={{ zIndex: 9999, maxWidth: 500, maxHeight: 280, overflowY: 'auto' }}
                  >
                    {searchResults.map((poi) => (
                      <li
                        key={poi.id}
                        className="list-group-item list-group-item-action py-2 px-3"
                        style={{ cursor: 'pointer', fontSize: 14 }}
                        onClick={() => handleSelectResult(poi)}
                      >
                        <div className="fw-medium">{poi.name}</div>
                        {poi.address && (
                          <div className="text-muted small">{poi.address}</div>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              {/* 地址详情输入框 */}
              <input
                type="text"
                name="address_text"
                className="form-control form-control-sm mb-2"
                value={form.address_text}
                onChange={(e) => {
                  setForm({ ...form, address_text: e.target.value });
                  setSearchQuery(e.target.value);
                }}
                required
                placeholder="详细地址（自动填写，可手动修改）"
              />
              {locationHint && <small className="text-muted d-block mb-2">{locationHint}</small>}
              {/* Leaflet 地图 */}
              <div
                ref={mapRef}
                style={{ width: '100%', height: 350, borderRadius: 8, border: '1px solid #ddd' }}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label">悬赏金额（元）</label>
              <input type="number" step="0.01" min="0" name="reward_amount" className="form-control" value={form.reward_amount} onChange={handleChange} />
            </div>
            <div className="col-md-6">
              <label className="form-label">联系电话</label>
              <input type="tel" name="contact_phone" className="form-control" value={form.contact_phone} onChange={handleChange} placeholder="可选" />
            </div>
            <div className="col-12">
              <label className="form-label">照片 <span className="text-danger">*</span> <small className="text-muted">(至少 1 张)</small></label>
              <input type="file" className="form-control" accept="image/*" multiple onChange={handlePhotoUpload} disabled={uploading} />
              {uploading && <small className="text-muted">上传中...</small>}
              {photoUrls.length > 0 && (
                <div className="d-flex flex-wrap gap-2 mt-2">
                  {photoUrls.map((url, idx) => (
                    <div key={url} className="position-relative">
                      <img src={url} alt="" style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 8 }} />
                      <button type="button" className="btn btn-danger btn-sm position-absolute top-0 end-0" style={{ padding: '0 4px', fontSize: 10 }} onClick={() => removePhoto(idx)}>×</button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="card-footer">
          {photoError && <div className="alert alert-danger py-2 mb-2">{photoError}</div>}
          <div className="d-flex gap-2">
          <button type="submit" className="btn btn-success" disabled={submitting || uploading}>
            {submitting ? '提交中...' : '发布'}
          </button>
          <Link to="/lost-found" className="btn btn-outline-secondary">取消</Link>
          </div>
        </div>
      </form>
    </div>
  );
};

export default LostFoundPublish;

