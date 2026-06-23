import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { adoptAPI, petsAPI, uploadAPI } from '../api/api';
import { ADOPTION_STATUS } from '../constants/site';

const SPECIES_LABELS = {
  dog: '狗',
  cat: '猫',
  bird: '鸟',
  rabbit: '兔',
  fish: '鱼',
  other: '其他',
};

const GENDER_LABELS = {
  male: '公',
  female: '母',
  unknown: '未知',
};

const formatAgeMonths = (months) => {
  if (months == null || months === '') return '未知';
  const m = Number(months);
  if (m < 12) return `${m}个月`;
  const years = Math.floor(m / 12);
  const rem = m % 12;
  if (rem === 0) return `${years}岁`;
  return `${years}岁${rem}个月`;
};

// 从详细地址中提取市级名称
const extractCity = (address) => {
  if (!address) return null;
  const idx = address.indexOf('市');
  if (idx !== -1) return address.substring(0, idx + 1);
  return address.length > 4 ? address.substring(0, 4) : address;
};

const ADOPTION_BADGE = {
  available: 'success',
  pending: 'warning text-dark',
  adopted: 'secondary',
};

const QUESTIONNAIRE_FIELDS = [
  { key: 'housing_type', label: '居住类型（公寓/独栋/其他）' },
  { key: 'has_other_pets', label: '是否已有其他宠物？（是/否）' },
  { key: 'experience', label: '养宠经验' },
  { key: 'daily_hours', label: '每日在家时长（小时）' },
  { key: 'family_agreement', label: '家人是否同意领养？（是/否）' },
];

const FILE_TYPE_LABELS = {
  id_card: '身份证',
  income_proof: '收入证明',
  housing_proof: '住房证明',
  other: '其他',
};

// 获取当前登录用户名
const getCurrentUsername = () => {
  try {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      return user.username || user.name || '访客';
    }
  } catch (e) { /* ignore */ }
  return '访客';
};

const PetDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pet, setPet] = useState(null);
  const [allPets, setAllPets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [username] = useState(getCurrentUsername());

  // 领养申请状态
  const [adoptStep, setAdoptStep] = useState(1);
  const [applicationId, setApplicationId] = useState(null);
  const [message, setMessage] = useState('');
  const [questionnaire, setQuestionnaire] = useState(
    QUESTIONNAIRE_FIELDS.reduce((acc, f) => ({ ...acc, [f.key]: '' }), {})
  );
  const [attachmentFile, setAttachmentFile] = useState(null);
  const [fileType, setFileType] = useState('id_card');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [showAdoptForm, setShowAdoptForm] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [petRes, allRes] = await Promise.all([
          petsAPI.getById(id),
          petsAPI.getAll({ adoption_status: 'available' }),
        ]);
        setPet(petRes.data);
        const list = Array.isArray(allRes.data) ? allRes.data : allRes.data.results || [];
        setAllPets(list);
      } catch (err) {
        setError('加载宠物详情失败，请稍后重试。');
        console.error('Error fetching pet:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  // 前后切换
  const currentIndex = allPets.findIndex((p) => p.id === parseInt(id));
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex >= 0 && currentIndex < allPets.length - 1;
  const prevPet = hasPrev ? allPets[currentIndex - 1] : null;
  const nextPet = hasNext ? allPets[currentIndex + 1] : null;

  const goToPrev = () => {
    if (prevPet) {
      setLoading(true);
      setShowAdoptForm(false);
      setAdoptStep(1);
      setSubmitError(null);
      setSubmitSuccess(false);
      navigate(`/pets/${prevPet.id}`);
    }
  };

  const goToNext = () => {
    if (nextPet) {
      setLoading(true);
      setShowAdoptForm(false);
      setAdoptStep(1);
      setSubmitError(null);
      setSubmitSuccess(false);
      navigate(`/pets/${nextPet.id}`);
    }
  };

  const requireAuth = () => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
      return false;
    }
    return true;
  };

  const handleStep1Submit = async (e) => {
    e.preventDefault();
    if (!requireAuth()) return;
    try {
      setSubmitting(true);
      setSubmitError(null);
      const response = await adoptAPI.create({ pet_id: pet.id, message });
      setApplicationId(response.data.id);
      setAdoptStep(2);
    } catch (err) {
      const detail = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0];
      setSubmitError(detail || '提交领养申请失败，请重试。');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStep2Submit = async (e) => {
    e.preventDefault();
    if (!requireAuth() || !applicationId) return;
    try {
      setSubmitting(true);
      setSubmitError(null);
      await adoptAPI.submitQuestionnaire(applicationId, questionnaire);
      setAdoptStep(3);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || '提交问卷失败，请重试。');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStep3Submit = async (e) => {
    e.preventDefault();
    if (!requireAuth() || !applicationId || !attachmentFile) {
      setSubmitError('请选择要上传的文件。');
      return;
    }
    try {
      setSubmitting(true);
      setSubmitError(null);
      const uploadResponse = await uploadAPI.upload(attachmentFile, 'adopt');
      await adoptAPI.addAttachment(applicationId, {
        file_type: fileType,
        file_url: uploadResponse.data.url,
        file_size: attachmentFile.size,
      });
      setSubmitSuccess(true);
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err) {
      setSubmitError('上传附件失败，请重试。');
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuestionnaireChange = (key, value) => {
    setQuestionnaire((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
        <p className="mt-2">正在加载宠物详情...</p>
      </div>
    );
  }

  if (error || !pet) {
    return (
      <div className="container py-4 text-center">
        <div className="alert alert-danger" role="alert">
          {error || '未找到该宠物。'}
        </div>
        <Link to="/pets" className="btn btn-outline-success">
          <i className="fas fa-arrow-left me-1"></i>返回宠物列表
        </Link>
      </div>
    );
  }

  const canAdopt = pet.adoption_status === 'available';
  const cityName = extractCity(pet.rescue_case_address);
  const petAge = formatAgeMonths(pet.age_months);

  return (
    <div className="pet-detail-page">
      {/* ===== 面包屑导航 ===== */}
      <div className="detail-breadcrumb">
        <div className="container">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb mb-0">
              <li className="breadcrumb-item"><Link to="/">首页</Link></li>
              <li className="breadcrumb-item"><Link to="/pets">领养列表</Link></li>
              <li className="breadcrumb-item active">{pet.name}</li>
            </ol>
          </nav>
        </div>
      </div>

      <div className="container py-4">
        {/* ===== 上半部分：照片（左）+ 问候语（右）===== */}
        <div className="row g-4">
          {/* 左侧：宠物照片 + 箭头 + 下方信息 */}
          <div className="col-lg-6">
            {/* 照片区域 */}
            <div className="detail-image-wrapper">
              <button
                className={`nav-arrow nav-arrow-left ${!hasPrev ? 'disabled' : ''}`}
                onClick={goToPrev}
                disabled={!hasPrev}
                title={hasPrev ? `上一个：${prevPet?.name}` : '已是第一个'}
              >
                <i className="fas fa-chevron-left"></i>
              </button>

              <img
                src={pet.photo_url || 'https://via.placeholder.com/600x400?text=Pet+Photo'}
                className="detail-image"
                alt={pet.name}
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/600x400?text=Pet+Photo';
                }}
              />

              <button
                className={`nav-arrow nav-arrow-right ${!hasNext ? 'disabled' : ''}`}
                onClick={goToNext}
                disabled={!hasNext}
                title={hasNext ? `下一个：${nextPet?.name}` : '已是最后一个'}
              >
                <i className="fas fa-chevron-right"></i>
              </button>

              {allPets.length > 1 && (
                <span className="nav-position-badge">
                  {currentIndex + 1} / {allPets.length}
                </span>
              )}

              {canAdopt && (
                <span className="detail-available-badge">
                  <i className="fas fa-heart me-1"></i>等待领养
                </span>
              )}
            </div>

            {/* 照片下方：宠物信息（中等字体） */}
            <div className="pet-info-below">
              <div className="pet-info-grid">
                <div className="info-item-inline">
                  <span className="inline-label">种类</span>
                  <span className="inline-value">{SPECIES_LABELS[pet.species] || pet.species || '未知'}</span>
                </div>
                <div className="info-item-inline">
                  <span className="inline-label">性别</span>
                  <span className="inline-value">{GENDER_LABELS[pet.gender] || pet.gender || '未知'}</span>
                </div>
                <div className="info-item-inline">
                  <span className="inline-label">年龄</span>
                  <span className="inline-value">{petAge}</span>
                </div>
                {(pet.size_category_display || pet.rescue_case_appearance) && (
                  <div className="info-item-inline">
                    <span className="inline-label">体型</span>
                    <span className="inline-value">{pet.size_category_display || pet.rescue_case_appearance}</span>
                  </div>
                )}
                {cityName && (
                  <div className="info-item-inline">
                    <span className="inline-label">地区</span>
                    <span className="inline-value">{cityName}</span>
                  </div>
                )}
                <div className="info-item-inline">
                  <span className="inline-label">健康</span>
                  <span className="inline-value">{pet.health_status || '未填写'}</span>
                </div>
                {pet.rescue_case && (
                  <div className="info-item-inline">
                    <span className="inline-label">救助编号</span>
                    <span className="inline-value">#{pet.rescue_case}</span>
                  </div>
                )}
              </div>
              <span className={`badge bg-${ADOPTION_BADGE[pet.adoption_status] || 'secondary'} status-badge-bottom`}>
                {ADOPTION_STATUS[pet.adoption_status] || pet.adoption_status}
              </span>
            </div>
          </div>

          {/* 右侧：四行问候语 + 带我回家 */}
          <div className="col-lg-6">
            <div className="greeting-card">
              <p className="greeting-line greeting-name">
                你好！<strong>{username}</strong>
              </p>
              <p className="greeting-line greeting-name">
                我是<strong>{pet.name}</strong>
              </p>
              <p className="greeting-line">
                我今年<strong>{petAge}</strong>啦！
              </p>
              <p className="greeting-line">
                我正身处于<strong>{cityName || '未知地区'}</strong>
              </p>

              <div className="greeting-actions mt-4">
                {canAdopt ? (
                  <button
                    className="btn btn-adopt btn-lg w-100"
                    onClick={() => {
                      if (!requireAuth()) return;
                      navigate(`/adopt/${pet.id}`);
                    }}
                  >
                    <i className="fas fa-home me-2"></i>带我回家
                  </button>
                ) : (
                  <div className="alert alert-info mb-0 text-center">
                    <i className="fas fa-info-circle me-2"></i>
                    该宠物当前不可领养
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ===== 捡拾详情描述（整行）===== */}
        <div className="detail-bottom-section mt-4">
          <div className="detail-description-card">
            <h4 className="section-title">
              <i className="fas fa-file-alt me-2"></i>捡拾详情描述
            </h4>
            <div className="section-content">
              {pet.description ? (
                <p className="description-text">{pet.description}</p>
              ) : (
                <p className="text-muted fst-italic">暂无详细描述信息。</p>
              )}
            </div>
          </div>
        </div>

        {/* ===== 领养申请表单（点击带我回家后才显示）===== */}
        {canAdopt && showAdoptForm && (
          <div id="adopt-form-section" className="adopt-form-section mt-4">
            <div className="adopt-form-card">
              <div className="adopt-form-header">
                <h4 className="mb-0">
                  <i className="fas fa-file-signature me-2"></i>领养申请表
                </h4>
                <small className="text-white-50">步骤 {adoptStep} / 3</small>
              </div>

              <div className="adopt-form-body">
                <div className="adopt-progress mb-4">
                  <div className="progress-steps">
                    <div className={`step ${adoptStep >= 1 ? 'active' : ''} ${adoptStep > 1 ? 'completed' : ''}`}>
                      <div className="step-circle">1</div>
                      <small>填写留言</small>
                    </div>
                    <div className={`step-line ${adoptStep > 1 ? 'completed' : ''}`}></div>
                    <div className={`step ${adoptStep >= 2 ? 'active' : ''} ${adoptStep > 2 ? 'completed' : ''}`}>
                      <div className="step-circle">2</div>
                      <small>完成问卷</small>
                    </div>
                    <div className={`step-line ${adoptStep > 2 ? 'completed' : ''}`}></div>
                    <div className={`step ${adoptStep >= 3 ? 'active' : ''}`}>
                      <div className="step-circle">3</div>
                      <small>上传材料</small>
                    </div>
                  </div>
                </div>

                {submitSuccess ? (
                  <div className="alert alert-success text-center py-4">
                    <i className="fas fa-check-circle fa-3x mb-3"></i>
                    <h5>申请提交成功！</h5>
                    <p className="mb-0">正在跳转到个人中心...</p>
                  </div>
                ) : (
                  <>
                    {adoptStep === 1 && (
                      <form onSubmit={handleStep1Submit}>
                        <div className="mb-3">
                          <label className="form-label fw-bold">
                            <i className="fas fa-heart me-1 text-danger"></i>
                            您为什么想领养 {pet.name}？
                          </label>
                          <textarea
                            className="form-control"
                            rows="4"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="请介绍您的领养意愿、家庭环境、养宠条件等..."
                            required
                          />
                          <small className="text-muted">
                            请详细说明您的情况，这将帮助我们评估您是否适合领养{pet.name}。
                          </small>
                        </div>
                        {submitError && <div className="alert alert-danger">{submitError}</div>}
                        <button type="submit" className="btn btn-success" disabled={submitting}>
                          {submitting ? '提交中...' : <><i className="fas fa-arrow-right me-1"></i>下一步：填写问卷</>}
                        </button>
                      </form>
                    )}

                    {adoptStep === 2 && (
                      <form onSubmit={handleStep2Submit}>
                        <p className="text-muted small mb-3">
                          <i className="fas fa-clipboard-list me-1"></i>请如实填写以下问卷，帮助我们了解您的领养条件。
                        </p>
                        {QUESTIONNAIRE_FIELDS.map((field) => (
                          <div className="mb-3" key={field.key}>
                            <label className="form-label">{field.label}</label>
                            <input
                              type="text"
                              className="form-control"
                              value={questionnaire[field.key]}
                              onChange={(e) => handleQuestionnaireChange(field.key, e.target.value)}
                              required
                            />
                          </div>
                        ))}
                        {submitError && <div className="alert alert-danger">{submitError}</div>}
                        <div className="d-flex justify-content-between">
                          <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={() => setAdoptStep(1)}
                            disabled={submitting}
                          >
                            <i className="fas fa-arrow-left me-1"></i>上一步
                          </button>
                          <button type="submit" className="btn btn-success" disabled={submitting}>
                            {submitting ? '提交中...' : <><i className="fas fa-arrow-right me-1"></i>下一步：上传材料</>}
                          </button>
                        </div>
                      </form>
                    )}

                    {adoptStep === 3 && (
                      <form onSubmit={handleStep3Submit}>
                        <p className="text-muted small mb-3">
                          <i className="fas fa-upload me-1"></i>请上传居民身份证及居住证明资料。
                        </p>
                        <div className="mb-3">
                          <label className="form-label">材料类型</label>
                          <select
                            className="form-select"
                            value={fileType}
                            onChange={(e) => setFileType(e.target.value)}
                          >
                            {Object.entries(FILE_TYPE_LABELS).map(([value, label]) => (
                              <option key={value} value={value}>{label}</option>
                            ))}
                          </select>
                        </div>
                        <div className="mb-3">
                          <label className="form-label">上传文件</label>
                          <input
                            type="file"
                            className="form-control"
                            accept="image/*,.pdf"
                            onChange={(e) => setAttachmentFile(e.target.files?.[0] || null)}
                            required
                          />
                          <small className="text-muted">支持 JPG、PNG、GIF、WEBP 或 PDF 格式</small>
                        </div>
                        {submitError && <div className="alert alert-danger">{submitError}</div>}
                        <div className="d-flex justify-content-between">
                          <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={() => setAdoptStep(2)}
                            disabled={submitting}
                          >
                            <i className="fas fa-arrow-left me-1"></i>上一步
                          </button>
                          <button type="submit" className="btn btn-adopt" disabled={submitting}>
                            {submitting ? '上传中...' : <><i className="fas fa-paper-plane me-1"></i>提交申请</>}
                          </button>
                        </div>
                      </form>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ===== 样式 ===== */}
      <style>{`
        .pet-detail-page {
          background-color: #FAFAFA;
          min-height: 100vh;
          padding-bottom: 3rem;
        }

        .detail-breadcrumb {
          background: white;
          border-bottom: 1px solid #eee;
          padding: 0.75rem 0;
        }
        .breadcrumb { font-size: 0.9rem; }

        /* ===== 照片 + 箭头 ===== */
        .detail-image-wrapper {
          position: relative;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
          user-select: none;
        }
        .detail-image {
          width: 100%;
          height: 420px;
          object-fit: cover;
          display: block;
        }

        .nav-arrow {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: none;
          background: rgba(255,255,255,0.85);
          color: #333;
          font-size: 1.1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          z-index: 10;
          transition: all 0.2s ease;
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .nav-arrow:hover:not(.disabled) {
          background: white;
          color: #00C897;
          box-shadow: 0 4px 15px rgba(0,0,0,0.2);
          transform: translateY(-50%) scale(1.1);
        }
        .nav-arrow-left  { left: 12px; }
        .nav-arrow-right { right: 12px; }
        .nav-arrow.disabled { opacity: 0.35; cursor: not-allowed; }

        .nav-position-badge {
          position: absolute;
          top: 12px;
          right: 12px;
          background: rgba(0,0,0,0.5);
          color: white;
          font-size: 0.75rem;
          padding: 0.25em 0.7em;
          border-radius: 15px;
          z-index: 10;
        }
        .detail-available-badge {
          position: absolute;
          bottom: 16px;
          left: 16px;
          background: linear-gradient(135deg, #00C897, #009B74);
          color: white;
          padding: 0.4em 1em;
          border-radius: 25px;
          font-size: 0.9rem;
          font-weight: 500;
          box-shadow: 0 2px 10px rgba(0,200,151,0.4);
        }

        /* ===== 照片下方宠物信息 ===== */
        .pet-info-below {
          background: white;
          border-radius: 12px;
          padding: 1rem 1.25rem;
          margin-top: 1rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .pet-info-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 0.4rem 1.5rem;
        }
        .info-item-inline {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          font-size: 0.95rem;
        }
        .info-item-inline .inline-label {
          color: #999;
        }
        .info-item-inline .inline-value {
          color: #333;
          font-weight: 500;
        }
        .status-badge-bottom {
          margin-top: 0.5rem;
          display: inline-block;
          font-size: 0.8rem;
          padding: 0.3em 0.8em;
          border-radius: 15px;
        }

        /* ===== 右侧问候卡片 ===== */
        .greeting-card {
          background: white;
          border-radius: 16px;
          padding: 2.5rem 2rem;
          box-shadow: 0 2px 12px rgba(0,0,0,0.06);
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        .greeting-line {
          font-size: 1.3rem;
          color: #555;
          margin-bottom: 1.2rem;
          line-height: 1.6;
        }
        .greeting-line strong {
          color: #222;
          font-size: 1.55rem;
        }
        .greeting-name {
          font-size: 1.5rem;
        }
        .greeting-name strong {
          font-size: 1.7rem;
          color: #00C897;
        }
        .greeting-actions {
          margin-top: auto;
          padding-top: 1.5rem;
        }

        /* 带我回家按钮 */
        .btn-adopt {
          background: linear-gradient(135deg, #00C897, #00A87A);
          border: none;
          color: white;
          font-size: 1.2rem;
          font-weight: 600;
          padding: 0.9rem;
          border-radius: 30px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(0, 200, 151, 0.3);
          letter-spacing: 1px;
        }
        .btn-adopt:hover {
          background: linear-gradient(135deg, #00B386, #00936A);
          transform: translateY(-3px);
          box-shadow: 0 8px 25px rgba(0, 200, 151, 0.4);
          color: white;
        }

        /* ===== 捡拾详情描述 ===== */
        .detail-description-card {
          background: white;
          border-radius: 16px;
          padding: 1.75rem;
          box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .section-title {
          font-size: 1.2rem;
          font-weight: 600;
          color: #333;
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
          border-bottom: 2px solid #e9ecef;
        }
        .section-title i { color: #00C897; }
        .description-text {
          color: #555;
          line-height: 1.8;
          font-size: 0.95rem;
        }

        /* ===== 领养表单 ===== */
        .adopt-form-section { scroll-margin-top: 2rem; }
        .adopt-form-card {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .adopt-form-header {
          background: linear-gradient(135deg, #00C897, #009B74);
          color: white;
          padding: 1.25rem 1.75rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .adopt-form-body { padding: 2rem; }

        .progress-steps {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .step {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.4rem;
        }
        .step-circle {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: #e9ecef;
          color: #999;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 0.9rem;
          transition: all 0.3s ease;
        }
        .step.active .step-circle { background: #00C897; color: white; }
        .step.completed .step-circle { background: #28a745; color: white; }
        .step small { color: #999; font-size: 0.75rem; }
        .step.active small { color: #00C897; font-weight: 600; }
        .step.completed small { color: #28a745; }
        .step-line {
          width: 50px;
          height: 3px;
          background: #e9ecef;
          margin: 0 0.5rem 1.5rem;
          border-radius: 2px;
          transition: all 0.3s ease;
        }
        .step-line.completed { background: #28a745; }
      `}</style>
    </div>
  );
};

export default PetDetail;
