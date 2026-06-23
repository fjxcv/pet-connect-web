import React, { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { rescueAPI, uploadAPI } from '../api/api';
import { SIZE_CATEGORY, HEALTH_STATUS } from '../constants/site';
import { formatApiError, roundCoordinate } from '../utils/apiError';

// 文件校验常量
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];
const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// 高德地图 API Key
const AMAP_KEY = '0cd985d74a8143ce3e159294a37635a2';

// 逆地理编码：通过高德 API 将经纬度转换为可读地址
const reverseGeocode = async (lat, lng) => {
  try {
    const res = await fetch(
      `https://restapi.amap.com/v3/geocode/regeo?key=${AMAP_KEY}&location=${lng},${lat}`,
    );
    if (!res.ok) return '';
    const data = await res.json();
    if (data.status === '1' && data.regeocode) {
      return data.regeocode.formatted_address || '';
    }
    return '';
  } catch {
    return '';
  }
};

const RescueReport = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [form, setForm] = useState({
    nickname: '',
    contact: '',
    discover_address: '',
    discover_latitude: '',
    discover_longitude: '',
    size_category: '',
    health_status: '',
    is_injured: '',
    afraid_of_people: '',
  });
  const [photos, setPhotos] = useState([]);  // { name, url, size }
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [locating, setLocating] = useState(false);
  const [locationHint, setLocationHint] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [successNo, setSuccessNo] = useState('');

  // ---- 表单字段处理 ----
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  // ---- 自动定位 + 逆地理编码 ----
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
        const meters = Math.round(pos.coords.accuracy);

        // 调用逆地理编码获取可读地址
        const geocoded = await reverseGeocode(lat, lng);

        setForm((prev) => ({
          ...prev,
          discover_latitude: String(lat),
          discover_longitude: String(lng),
          discover_address: geocoded
            ? geocoded
            : '当前位置',
        }));

        if (geocoded) {
          setLocationHint(`已定位并解析地址（精度约 ${meters} 米），可在此基础上修改。`);
        } else {
          setLocationHint(`已记录坐标（精度约 ${meters} 米），未能解析地名，请手动填写详细地址。`);
        }
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

  // ---- 照片上传 ----
  const handlePhotoSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    for (const f of files) {
      const ext = '.' + f.name.split('.').pop().toLowerCase();
      if (!ALLOWED_TYPES.includes(f.type) && !ALLOWED_EXTENSIONS.includes(ext)) {
        setError(`文件 "${f.name}" 格式不支持，仅支持 jpg、png、pdf。`);
        e.target.value = '';
        return;
      }
      if (f.size > MAX_FILE_SIZE) {
        setError(`文件 "${f.name}" 超过 5MB 限制。`);
        e.target.value = '';
        return;
      }
    }

    setUploading(true);
    setError('');
    try {
      const uploaded = [];
      for (const f of files) {
        const res = await uploadAPI.upload(f, 'rescue');
        uploaded.push({ name: f.name, url: res.data.url, size: f.size });
      }
      setPhotos((prev) => [...prev, ...uploaded]);
    } catch (err) {
      setError('图片上传失败，请重试。');
      console.error(err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const removePhoto = (index) => {
    setPhotos((prev) => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  // ---- 表单校验 ----
  const validate = () => {
    const errs = {};
    if (!form.nickname.trim()) errs.nickname = '请填写您的昵称';
    if (!form.contact.trim()) {
      errs.contact = '请填写您的联系方式';
    } else if (form.contact.trim().length < 5) {
      errs.contact = '联系方式格式不正确，请填写手机号或微信号';
    }
    if (!form.discover_address.trim()) errs.discover_address = '请填写发现的详细位置';
    if (!form.size_category) errs.size_category = '请选择体型描述';
    if (!form.health_status) errs.health_status = '请选择健康状况';
    if (form.is_injured === '' || form.is_injured === null) errs.is_injured = '请选择是否受伤';
    if (form.afraid_of_people === '' || form.afraid_of_people === null) errs.afraid_of_people = '请选择是否怕人';
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // ---- 提交 ----
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!validate()) return;

    setSubmitting(true);
    try {
      const lat = roundCoordinate(form.discover_latitude);
      const lng = roundCoordinate(form.discover_longitude);
      const payload = {
        nickname: form.nickname.trim(),
        contact: form.contact.trim(),
        discover_address: form.discover_address.trim(),
        appearance: `体型: ${SIZE_CATEGORY[form.size_category] || form.size_category} / 健康: ${HEALTH_STATUS[form.health_status] || form.health_status} / 受伤: ${form.is_injured === 'yes' ? '是' : '否'} / 怕人: ${form.afraid_of_people === 'yes' ? '是' : '否'}`,
        size_category: form.size_category,
        health_status: form.health_status,
        is_injured: form.is_injured === 'yes',
        afraid_of_people: form.afraid_of_people === 'yes',
        photo_urls: photos.map((p) => p.url),
      };
      if (lat != null && lng != null) {
        payload.discover_latitude = lat;
        payload.discover_longitude = lng;
      }
      const res = await rescueAPI.create(payload);
      setSuccessNo(res.data.rescue_no);
    } catch (err) {
      setError(formatApiError(err, '提交失败，请检查表单后重试。'));
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setForm({
      nickname: '',
      contact: '',
      discover_address: '',
      discover_latitude: '',
      discover_longitude: '',
      size_category: '',
      health_status: '',
      is_injured: '',
      afraid_of_people: '',
    });
    setPhotos([]);
    setError('');
    setFieldErrors({});
    setSuccessNo('');
  };

  // ---- 成功页 ----
  if (successNo) {
    return (
      <div className="py-3">
        <div className="text-center py-5">
          <i className="fas fa-check-circle fa-4x text-success mb-3"></i>
          <h3>提交成功！</h3>
          <p className="text-muted mb-2">您的救助编号为：</p>
          <h2 className="text-success fw-bold mb-3">{successNo}</h2>
          <p className="text-muted mb-4">请妥善保管此编号，后续可通过编号查询救助进度。</p>
          <div className="d-flex justify-content-center gap-2">
            <button className="btn btn-success" onClick={handleReset}>
              <i className="fas fa-plus me-1"></i>继续上报
            </button>
            <button className="btn btn-outline-success" onClick={() => navigate('/rescue')}>
              <i className="fas fa-list me-1"></i>返回列表
            </button>
          </div>
        </div>
      </div>
    );
  }

  const labelCol = 'col-sm-2 col-form-label';
  const inputCol = 'col-sm-10';

  return (
    <div className="py-3">
      {/* 面包屑 */}
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/rescue">救助追踪</Link></li>
          <li className="breadcrumb-item active">流浪动物发现上报</li>
        </ol>
      </nav>

      <h2 className="mb-4"><i className="fas fa-clipboard-list me-2 text-success"></i>流浪动物发现上报</h2>

      {error && (
        <div className="alert alert-danger d-flex align-items-center gap-2">
          <i className="fas fa-exclamation-triangle"></i>
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card shadow-sm" noValidate>
        <div className="card-body">

          {/* 您的昵称 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>您的昵称 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <input
                type="text"
                name="nickname"
                className={`form-control ${fieldErrors.nickname ? 'is-invalid' : ''}`}
                value={form.nickname}
                onChange={handleChange}
                placeholder="请输入您的昵称"
                maxLength={50}
              />
            </div>
            {fieldErrors.nickname && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.nickname}</div>
              </div>
            )}
          </div>

          {/* 您的联系方式 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>您的联系方式 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <input
                type="text"
                name="contact"
                className={`form-control ${fieldErrors.contact ? 'is-invalid' : ''}`}
                value={form.contact}
                onChange={handleChange}
                placeholder="手机号或微信号"
                maxLength={100}
              />
              <small className="text-muted">建议填写手机号或微信号，方便其他救助者与您联系</small>
            </div>
            {fieldErrors.contact && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.contact}</div>
              </div>
            )}
          </div>

          {/* 发现的详细位置 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>发现的详细位置 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <div className="input-group">
                <input
                  type="text"
                  name="discover_address"
                  className={`form-control ${fieldErrors.discover_address ? 'is-invalid' : ''}`}
                  value={form.discover_address}
                  onChange={handleChange}
                  placeholder="如：XX 大学南门、XX 小区北门公交站"
                />
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={handleUseCurrentLocation}
                  disabled={locating || submitting}
                  title="自动定位当前位置"
                >
                  {locating ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
                      定位中...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-location-crosshairs me-1"></i>
                      定位
                    </>
                  )}
                </button>
              </div>
              {locationHint && (
                <small className={`d-block mt-1 ${locationHint.includes('未能') ? 'text-warning' : 'text-success'}`}>
                  <i className={`fas fa-${locationHint.includes('未能') ? 'exclamation-circle' : 'check-circle'} me-1`}></i>
                  {locationHint}
                </small>
              )}
            </div>
            {fieldErrors.discover_address && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.discover_address}</div>
              </div>
            )}
          </div>

          {/* 上传动物照片 */}
          <div className="row mb-3">
            <label className={`${labelCol} fw-bold pt-2`}>上传动物照片</label>
            <div className={inputCol}>
              <div
                className="border border-2 rounded-3 p-4 text-center"
                style={{
                  borderStyle: 'dashed',
                  cursor: 'pointer',
                  minHeight: 160,
                  backgroundColor: photos.length > 0 ? '#fafafa' : '#fdfdfd',
                }}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  className="d-none"
                  accept=".jpg,.jpeg,.png,.pdf"
                  multiple
                  onChange={handlePhotoSelect}
                  disabled={uploading || submitting}
                />

                {uploading ? (
                  <div className="py-4">
                    <span className="spinner-border text-success" role="status" />
                    <p className="text-muted mt-2 mb-0">上传中...</p>
                  </div>
                ) : photos.length === 0 ? (
                  <div className="py-3">
                    <div
                      className="d-inline-flex align-items-center justify-content-center rounded-circle mb-3"
                      style={{
                        width: 56,
                        height: 56,
                        backgroundColor: '#e8f5e9',
                        color: '#4caf50',
                        fontSize: 28,
                      }}
                    >
                      <i className="fas fa-plus"></i>
                    </div>
                    <p className="mb-1" style={{ color: '#333', fontWeight: 500 }}>点击上传照片</p>
                    <p className="text-muted mb-0" style={{ fontSize: '0.8rem' }}>
                      支持 jpg、png、pdf，单文件不超过 5MB
                    </p>
                  </div>
                ) : (
                  <div>
                    <div className="d-flex flex-wrap justify-content-center gap-3 mb-3">
                      {photos.map((photo, idx) => (
                        <div
                          key={idx}
                          className="position-relative border rounded overflow-hidden bg-white"
                          style={{ width: 120 }}
                        >
                          {photo.url.toLowerCase().endsWith('.pdf') ? (
                            <div className="d-flex flex-column align-items-center justify-content-center" style={{ height: 100 }}>
                              <i className="fas fa-file-pdf fa-2x text-danger"></i>
                              <small className="text-muted text-truncate w-100 px-1 text-center" title={photo.name}>{photo.name}</small>
                            </div>
                          ) : (
                            <img
                              src={photo.url}
                              alt={photo.name}
                              style={{ width: '100%', height: 100, objectFit: 'cover' }}
                            />
                          )}
                          <div className="p-1" style={{ fontSize: '0.7rem' }}>
                            <div className="text-truncate" title={photo.name}>{photo.name}</div>
                            <div className="text-muted">{formatFileSize(photo.size)}</div>
                          </div>
                          <button
                            type="button"
                            className="btn btn-danger btn-sm position-absolute"
                            style={{ top: 2, right: 2, padding: '0 5px', fontSize: 12, borderRadius: '50%', width: 22, height: 22, lineHeight: 1 }}
                            onClick={(e) => { e.stopPropagation(); removePhoto(idx); }}
                            title="删除此文件"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                    <button
                      type="button"
                      className="btn btn-outline-success btn-sm"
                      onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                    >
                      <i className="fas fa-plus me-1"></i>继续添加
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 体型描述 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>体型描述 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <div className={`d-flex gap-3 ${fieldErrors.size_category ? 'border border-danger rounded p-2' : ''}`}>
                {Object.entries(SIZE_CATEGORY).map(([key, label]) => (
                  <div className="form-check" key={key}>
                    <input
                      className="form-check-input"
                      type="radio"
                      name="size_category"
                      id={`size_${key}`}
                      value={key}
                      checked={form.size_category === key}
                      onChange={handleChange}
                    />
                    <label className="form-check-label" htmlFor={`size_${key}`}>{label}</label>
                  </div>
                ))}
              </div>
            </div>
            {fieldErrors.size_category && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.size_category}</div>
              </div>
            )}
          </div>

          {/* 健康状况 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>健康状况 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <div className={`d-flex gap-3 ${fieldErrors.health_status ? 'border border-danger rounded p-2' : ''}`}>
                {Object.entries(HEALTH_STATUS).map(([key, label]) => (
                  <div className="form-check" key={key}>
                    <input
                      className="form-check-input"
                      type="radio"
                      name="health_status"
                      id={`health_${key}`}
                      value={key}
                      checked={form.health_status === key}
                      onChange={handleChange}
                    />
                    <label className="form-check-label" htmlFor={`health_${key}`}>{label}</label>
                  </div>
                ))}
              </div>
            </div>
            {fieldErrors.health_status && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.health_status}</div>
              </div>
            )}
          </div>

          {/* 是否受伤 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>是否受伤 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <div className={`d-flex gap-3 ${fieldErrors.is_injured ? 'border border-danger rounded p-2' : ''}`}>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="is_injured"
                    id="injured_yes"
                    value="yes"
                    checked={form.is_injured === 'yes'}
                    onChange={handleChange}
                  />
                  <label className="form-check-label" htmlFor="injured_yes">是</label>
                </div>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="is_injured"
                    id="injured_no"
                    value="no"
                    checked={form.is_injured === 'no'}
                    onChange={handleChange}
                  />
                  <label className="form-check-label" htmlFor="injured_no">否</label>
                </div>
              </div>
            </div>
            {fieldErrors.is_injured && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.is_injured}</div>
              </div>
            )}
          </div>

          {/* 是否怕人 */}
          <div className="row mb-3 align-items-center">
            <label className={`${labelCol} fw-bold`}>是否怕人 <span className="text-danger">*</span></label>
            <div className={inputCol}>
              <div className={`d-flex gap-3 ${fieldErrors.afraid_of_people ? 'border border-danger rounded p-2' : ''}`}>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="afraid_of_people"
                    id="afraid_yes"
                    value="yes"
                    checked={form.afraid_of_people === 'yes'}
                    onChange={handleChange}
                  />
                  <label className="form-check-label" htmlFor="afraid_yes">是</label>
                </div>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="afraid_of_people"
                    id="afraid_no"
                    value="no"
                    checked={form.afraid_of_people === 'no'}
                    onChange={handleChange}
                  />
                  <label className="form-check-label" htmlFor="afraid_no">否</label>
                </div>
              </div>
            </div>
            {fieldErrors.afraid_of_people && (
              <div className="offset-sm-2 col-sm-10">
                <div className="invalid-feedback d-block">{fieldErrors.afraid_of_people}</div>
              </div>
            )}
          </div>

        </div>

        {/* 底部按钮 */}
        <div className="card-footer d-flex justify-content-center gap-2">
          <button
            type="submit"
            className="btn btn-success"
            disabled={submitting || uploading}
          >
            {submitting ? (
              <>
                <span className="spinner-border spinner-border-sm me-1" />
                提交中...
              </>
            ) : (
              <>
                <i className="fas fa-paper-plane me-1"></i>提交
              </>
            )}
          </button>
          <Link to="/rescue" className="btn btn-outline-secondary">取消</Link>
        </div>
      </form>
    </div>
  );
};

export default RescueReport;
