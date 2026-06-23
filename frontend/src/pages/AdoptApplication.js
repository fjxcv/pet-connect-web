import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { adoptAPI, petsAPI, uploadAPI } from '../api/api';

const GENDER_OPTIONS = [
  { value: '', label: '请选择' },
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'undisclosed', label: '不愿透露' },
];

const HOUSING_TYPE_OPTIONS = [
  { value: 'villa', label: '别墅' },
  { value: 'apartment', label: '普通住宅' },
  { value: 'courtyard', label: '乡村庭院' },
  { value: 'farm', label: '农场' },
  { value: 'other', label: '其他' },
];

const OWN_RENT_OPTIONS = [
  { value: 'own', label: '自有房' },
  { value: 'rent', label: '租房' },
];

const OUTDOOR_AREA_OPTIONS = [
  { value: 'yard', label: '院子或后院' },
  { value: 'park', label: '家附近的公园' },
  { value: 'rooftop', label: '屋顶和停车场' },
  { value: 'other', label: '其他' },
];

const YES_NO_OPTIONS = [
  { value: 'yes', label: '是' },
  { value: 'no', label: '否' },
];

const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];
const ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

const INITIAL_FORM = {
  full_name: '',
  address: '',
  phone: '',
  wechat: '',
  gender: '',
  age: '',
  housing_type: '',
  housing_type_other: '',
  own_or_rent: '',
  outdoor_areas: [],
  outdoor_areas_other: '',
  roommate_consent: '',
  has_pet_experience: '',
  pet_experience_desc: '',
  future_changes: '',
};

const AdoptApplication = () => {
  const { petId } = useParams();
  const navigate = useNavigate();
  const [pet, setPet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 步骤控制：1=问卷, 2=上传, 3=成功
  const [step, setStep] = useState(1);
  const [applicationId, setApplicationId] = useState(null);

  // 步骤1：表单
  const [form, setForm] = useState({ ...INITIAL_FORM });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // 步骤2：文件上传
  const [idCardFile, setIdCardFile] = useState(null);
  const [housingProofFile, setHousingProofFile] = useState(null);
  const [fileErrors, setFileErrors] = useState({});
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const idCardInputRef = useRef(null);
  const housingProofInputRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchPet = async () => {
      try {
        setLoading(true);
        const res = await petsAPI.getById(petId);
        setPet(res.data);
        if (res.data.adoption_status !== 'available') {
          setError('该宠物当前不可领养。');
        }
      } catch (err) {
        setError('加载宠物信息失败，请稍后重试。');
        console.error('Error fetching pet:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPet();
  }, [petId, navigate]);

  // ===== 步骤1：表单处理 =====

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleOutdoorAreaToggle = (value) => {
    setForm((prev) => {
      const areas = prev.outdoor_areas.includes(value)
        ? prev.outdoor_areas.filter((v) => v !== value)
        : [...prev.outdoor_areas, value];
      return { ...prev, outdoor_areas: areas };
    });
  };

  const validateStep1 = () => {
    const newErrors = {};
    if (!form.full_name.trim()) newErrors.full_name = '请填写姓名';
    if (!form.address.trim()) newErrors.address = '请填写地址';
    if (!form.phone.trim()) {
      newErrors.phone = '请填写电话号码';
    } else if (!/^[\d\-+() ]{7,20}$/.test(form.phone.trim())) {
      newErrors.phone = '请输入有效的电话号码';
    }
    if (!form.wechat.trim()) newErrors.wechat = '请填写微信号';
    if (!form.gender) newErrors.gender = '请选择性别';
    if (!form.age) {
      newErrors.age = '请填写年龄';
    } else if (!/^\d+$/.test(form.age) || parseInt(form.age) < 0 || parseInt(form.age) > 150) {
      newErrors.age = '请输入有效的年龄（0-150）';
    }
    if (!form.housing_type) newErrors.housing_type = '请选择住宅类型';
    if (form.housing_type === 'other' && !form.housing_type_other.trim()) {
      newErrors.housing_type_other = '请填写其他住宅类型';
    }
    if (!form.own_or_rent) newErrors.own_or_rent = '请选择住房情况';
    if (form.outdoor_areas.length === 0) newErrors.outdoor_areas = '请至少选择一个户外区域';
    if (form.outdoor_areas.includes('other') && !form.outdoor_areas_other.trim()) {
      newErrors.outdoor_areas_other = '请填写其他户外区域';
    }
    if (!form.roommate_consent) newErrors.roommate_consent = '请选择同住人/房东是否同意';
    if (!form.has_pet_experience) newErrors.has_pet_experience = '请选择是否养过宠物';
    if (form.has_pet_experience === 'yes' && !form.pet_experience_desc.trim()) {
      newErrors.pet_experience_desc = '请描述您的养宠经历';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleStep1Submit = async (e) => {
    e.preventDefault();
    if (!validateStep1()) return;

    try {
      setSubmitting(true);
      setSubmitError(null);

      const answers = { ...form };
      if (answers.housing_type !== 'other') delete answers.housing_type_other;
      if (!answers.outdoor_areas.includes('other')) delete answers.outdoor_areas_other;
      if (answers.has_pet_experience !== 'yes') delete answers.pet_experience_desc;

      const appRes = await adoptAPI.create({
        pet_id: parseInt(petId),
        message: `领养申请 - ${pet?.name || ''}`,
      });

      await adoptAPI.submitQuestionnaire(appRes.data.id, answers);
      setApplicationId(appRes.data.id);
      setStep(2);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      const detail = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0];
      setSubmitError(detail || '提交领养申请失败，请重试。');
      console.error('Error submitting adoption application:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // ===== 步骤2：文件上传处理 =====

  const validateFile = (file, fieldName) => {
    if (!file) return '请选择文件';
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_FILE_EXTENSIONS.includes(ext)) {
      return '仅支持 jpg、png、pdf 格式';
    }
    if (file.size > MAX_FILE_SIZE) {
      return '文件大小不能超过 5MB';
    }
    return null;
  };

  const handleIdCardSelect = (e) => {
    const file = e.target.files?.[0] || null;
    setIdCardFile(file);
    if (file && fileErrors.id_card) {
      setFileErrors((prev) => ({ ...prev, id_card: null }));
    }
  };

  const handleHousingProofSelect = (e) => {
    const file = e.target.files?.[0] || null;
    setHousingProofFile(file);
    if (file && fileErrors.housing_proof) {
      setFileErrors((prev) => ({ ...prev, housing_proof: null }));
    }
  };

  const handleStep2Submit = async (e) => {
    e.preventDefault();

    const newFileErrors = {};
    const idErr = validateFile(idCardFile, 'id_card');
    const housingErr = validateFile(housingProofFile, 'housing_proof');
    if (idErr) newFileErrors.id_card = idErr;
    if (housingErr) newFileErrors.housing_proof = housingErr;
    setFileErrors(newFileErrors);
    if (Object.keys(newFileErrors).length > 0) return;

    try {
      setUploading(true);
      setUploadError(null);

      // 上传身份证
      const idUploadRes = await uploadAPI.upload(idCardFile, 'adopt');
      await adoptAPI.addAttachment(applicationId, {
        file_type: 'id_card',
        file_url: idUploadRes.data.url,
        file_size: idCardFile.size,
      });

      // 上传居住证明
      const housingUploadRes = await uploadAPI.upload(housingProofFile, 'adopt');
      await adoptAPI.addAttachment(applicationId, {
        file_type: 'housing_proof',
        file_url: housingUploadRes.data.url,
        file_size: housingProofFile.size,
      });

      setStep(3);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setUploadError('上传文件失败，请重试。');
      console.error('Error uploading files:', err);
    } finally {
      setUploading(false);
    }
  };

  // ===== 渲染 =====

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
        <p className="mt-2">正在加载...</p>
      </div>
    );
  }

  if (error && !pet) {
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

  return (
    <div className="adopt-application-page">
      {/* ===== 面包屑导航 ===== */}
      <div className="detail-breadcrumb">
        <div className="container">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb mb-0">
              <li className="breadcrumb-item"><Link to="/">首页</Link></li>
              <li className="breadcrumb-item"><Link to="/pets">领养列表</Link></li>
              <li className="breadcrumb-item"><Link to={`/pets/${petId}`}>{pet?.name || '宠物详情'}</Link></li>
              <li className="breadcrumb-item active" aria-current="page">领养申请</li>
            </ol>
          </nav>
        </div>
      </div>

      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-lg-10 col-xl-9">
            {/* ===== 页面标题行 + 步骤指示器 ===== */}
            <div className="page-header-row">
              <h3 className="page-title mb-0">
                <i className="fas fa-paw me-2 text-success"></i>
                为 <strong>{pet?.name}</strong> 填写领养申请
              </h3>
              <div className="step-indicator">
                <div className={`step-dot ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
                  <span className="step-dot-num">1</span>
                </div>
                <span className={`step-dot-label ${step >= 1 ? 'active' : ''}`}>填写信息</span>
                <div className={`step-connector ${step >= 2 ? 'completed' : ''}`}></div>
                <div className={`step-dot ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
                  <span className="step-dot-num">2</span>
                </div>
                <span className={`step-dot-label ${step >= 2 ? 'active' : ''}`}>上传材料</span>
                <div className={`step-connector ${step >= 3 ? 'completed' : ''}`}></div>
                <div className={`step-dot ${step >= 3 ? 'active' : ''}`}>
                  <span className="step-dot-num">3</span>
                </div>
                <span className={`step-dot-label ${step >= 3 ? 'active' : ''}`}>完成</span>
              </div>
            </div>

            {/* ===== 步骤1：问卷表单 ===== */}
            {step === 1 && (
              <div className="form-card">
                <div className="form-card-header">
                  <h4 className="mb-0">
                    <i className="fas fa-file-signature me-2"></i>领养申请表
                  </h4>
                  <small className="text-white-50">步骤 1 / 2</small>
                </div>
                <div className="form-card-body">
                  <form onSubmit={handleStep1Submit} noValidate>
                    {/* 1. 姓名 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">1</span> 姓名
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <input
                        type="text"
                        className={`form-control form-control-lg ${errors.full_name ? 'is-invalid' : ''}`}
                        placeholder="请填写全名"
                        value={form.full_name}
                        onChange={(e) => handleChange('full_name', e.target.value)}
                      />
                      {errors.full_name && <div className="invalid-feedback d-block">{errors.full_name}</div>}
                    </div>

                    {/* 2. 地址 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">2</span> 未来您和狗狗居住的地址
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <input
                        type="text"
                        className={`form-control form-control-lg ${errors.address ? 'is-invalid' : ''}`}
                        placeholder="请输入您的详细地址"
                        value={form.address}
                        onChange={(e) => handleChange('address', e.target.value)}
                      />
                      {errors.address && <div className="invalid-feedback d-block">{errors.address}</div>}
                    </div>

                    {/* 3. 电话 + 微信 */}
                    <div className="row mb-4">
                      <div className="col-md-6">
                        <div className="form-field">
                          <label className="form-label-lg">
                            <span className="field-number">3</span> 您的电话
                            <span className="text-danger ms-1">*</span>
                          </label>
                          <input
                            type="tel"
                            className={`form-control form-control-lg ${errors.phone ? 'is-invalid' : ''}`}
                            placeholder="请输入您的电话号码"
                            value={form.phone}
                            onChange={(e) => handleChange('phone', e.target.value)}
                          />
                          {errors.phone && <div className="invalid-feedback d-block">{errors.phone}</div>}
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="form-field">
                          <label className="form-label-lg">
                            微信号
                            <span className="text-danger ms-1">*</span>
                          </label>
                          <input
                            type="text"
                            className={`form-control form-control-lg ${errors.wechat ? 'is-invalid' : ''}`}
                            placeholder="请输入您的微信号"
                            value={form.wechat}
                            onChange={(e) => handleChange('wechat', e.target.value)}
                          />
                          {errors.wechat && <div className="invalid-feedback d-block">{errors.wechat}</div>}
                        </div>
                      </div>
                    </div>

                    {/* 4. 性别 / 年龄 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">4</span> 性别 / 年龄
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <div className="row g-3">
                        <div className="col-md-6">
                          <select
                            className={`form-select form-control-lg ${errors.gender ? 'is-invalid' : ''}`}
                            value={form.gender}
                            onChange={(e) => handleChange('gender', e.target.value)}
                          >
                            {GENDER_OPTIONS.map((opt) => (
                              <option key={opt.value} value={opt.value} disabled={opt.value === ''}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                          {errors.gender && <div className="invalid-feedback d-block">{errors.gender}</div>}
                        </div>
                        <div className="col-md-6">
                          <input
                            type="number"
                            className={`form-control form-control-lg ${errors.age ? 'is-invalid' : ''}`}
                            placeholder="请输入您的年龄"
                            value={form.age}
                            onChange={(e) => handleChange('age', e.target.value)}
                            min="0"
                            max="150"
                            step="1"
                          />
                          {errors.age && <div className="invalid-feedback d-block">{errors.age}</div>}
                        </div>
                      </div>
                    </div>

                    {/* 5. 住宅类型 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">5</span> 您的住宅类型？
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <div className="radio-group">
                        {HOUSING_TYPE_OPTIONS.map((opt) => (
                          <label key={opt.value} className="radio-card">
                            <input
                              type="radio"
                              name="housing_type"
                              value={opt.value}
                              checked={form.housing_type === opt.value}
                              onChange={(e) => handleChange('housing_type', e.target.value)}
                            />
                            <span className="radio-card-label">{opt.label}</span>
                          </label>
                        ))}
                      </div>
                      {errors.housing_type && <div className="text-danger small mt-1">{errors.housing_type}</div>}
                      {form.housing_type === 'other' && (
                        <input
                          type="text"
                          className={`form-control mt-2 ${errors.housing_type_other ? 'is-invalid' : ''}`}
                          placeholder="请描述您的住宅类型"
                          value={form.housing_type_other}
                          onChange={(e) => handleChange('housing_type_other', e.target.value)}
                        />
                      )}
                      {errors.housing_type_other && <div className="invalid-feedback d-block">{errors.housing_type_other}</div>}
                    </div>

                    {/* 6. 自有房还是租房 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">6</span> 您是自有房屋还是租房族？
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <div className="radio-group">
                        {OWN_RENT_OPTIONS.map((opt) => (
                          <label key={opt.value} className="radio-card">
                            <input
                              type="radio"
                              name="own_or_rent"
                              value={opt.value}
                              checked={form.own_or_rent === opt.value}
                              onChange={(e) => handleChange('own_or_rent', e.target.value)}
                            />
                            <span className="radio-card-label">{opt.label}</span>
                          </label>
                        ))}
                      </div>
                      {errors.own_or_rent && <div className="text-danger small mt-1">{errors.own_or_rent}</div>}
                    </div>

                    {/* 7. 户外区域 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">7</span> 您可以带狗狗去的户外区域？
                        <span className="text-muted fw-normal small">（可多选）</span>
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <div className="checkbox-group">
                        {OUTDOOR_AREA_OPTIONS.map((opt) => (
                          <label key={opt.value} className="checkbox-card">
                            <input
                              type="checkbox"
                              value={opt.value}
                              checked={form.outdoor_areas.includes(opt.value)}
                              onChange={() => handleOutdoorAreaToggle(opt.value)}
                            />
                            <span className="checkbox-card-label">{opt.label}</span>
                          </label>
                        ))}
                      </div>
                      {errors.outdoor_areas && <div className="text-danger small mt-1">{errors.outdoor_areas}</div>}
                      {form.outdoor_areas.includes('other') && (
                        <input
                          type="text"
                          className={`form-control mt-2 ${errors.outdoor_areas_other ? 'is-invalid' : ''}`}
                          placeholder="请描述其他户外区域"
                          value={form.outdoor_areas_other}
                          onChange={(e) => handleChange('outdoor_areas_other', e.target.value)}
                        />
                      )}
                      {errors.outdoor_areas_other && <div className="invalid-feedback d-block">{errors.outdoor_areas_other}</div>}
                    </div>

                    {/* 8. 同住人/房东是否同意 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">8</span> 同住人/房东是否同意？
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <div className="radio-group">
                        {YES_NO_OPTIONS.map((opt) => (
                          <label key={opt.value} className="radio-card">
                            <input
                              type="radio"
                              name="roommate_consent"
                              value={opt.value}
                              checked={form.roommate_consent === opt.value}
                              onChange={(e) => handleChange('roommate_consent', e.target.value)}
                            />
                            <span className="radio-card-label">{opt.label}</span>
                          </label>
                        ))}
                      </div>
                      {errors.roommate_consent && <div className="text-danger small mt-1">{errors.roommate_consent}</div>}
                    </div>

                    {/* 9. 是否养过宠物 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">9</span> 是否养过宠物？
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <div className="radio-group">
                        {YES_NO_OPTIONS.map((opt) => (
                          <label key={opt.value} className="radio-card">
                            <input
                              type="radio"
                              name="has_pet_experience"
                              value={opt.value}
                              checked={form.has_pet_experience === opt.value}
                              onChange={(e) => handleChange('has_pet_experience', e.target.value)}
                            />
                            <span className="radio-card-label">{opt.label}</span>
                          </label>
                        ))}
                      </div>
                      {errors.has_pet_experience && <div className="text-danger small mt-1">{errors.has_pet_experience}</div>}
                      {form.has_pet_experience === 'yes' && (
                        <div className="mt-2">
                          <textarea
                            className={`form-control ${errors.pet_experience_desc ? 'is-invalid' : ''}`}
                            rows="3"
                            placeholder="请描述您之前的养宠经历（宠物种类、养了多久等）"
                            value={form.pet_experience_desc}
                            onChange={(e) => handleChange('pet_experience_desc', e.target.value)}
                          />
                          {errors.pet_experience_desc && <div className="invalid-feedback d-block">{errors.pet_experience_desc}</div>}
                        </div>
                      )}
                    </div>

                    {/* 10. 未来6个月变化 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">10</span> 您预计在接下来的6个月内会有任何较大的变化吗？请描述
                      </label>
                      <small className="text-muted d-block mb-1">例如，搬家、换工作、长期旅行</small>
                      <textarea
                        className="form-control"
                        rows="3"
                        placeholder="请描述您未来6个月内可能的变化（选填）"
                        value={form.future_changes}
                        onChange={(e) => handleChange('future_changes', e.target.value)}
                      />
                    </div>

                    {submitError && (
                      <div className="alert alert-danger">
                        <i className="fas fa-exclamation-circle me-2"></i>{submitError}
                      </div>
                    )}

                    <div className="form-actions">
                      <button
                        type="submit"
                        className="btn btn-submit btn-lg w-100"
                        disabled={submitting}
                      >
                        {submitting ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            提交中...
                          </>
                        ) : (
                          <>
                            下一步 <i className="fas fa-arrow-right ms-2"></i>
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* ===== 步骤2：文件上传 ===== */}
            {step === 2 && (
              <div className="form-card">
                <div className="form-card-header">
                  <h4 className="mb-0">
                    <i className="fas fa-upload me-2"></i>上传证明材料
                  </h4>
                  <small className="text-white-50">步骤 2 / 2</small>
                </div>
                <div className="form-card-body">
                  <form onSubmit={handleStep2Submit} noValidate>
                    {/* 提示信息 */}
                    <div className="upload-intro mb-4">
                      <i className="fas fa-info-circle me-2 text-success"></i>
                      请上传以下证明材料，以便工作人员审核您的领养资格。
                    </div>

                    {/* a) 居民身份证 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">a</span> 请上传您的居民身份证
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <p className="text-muted small mb-2">
                        点击上传您的居民身份证（支持 jpg、png、pdf，单文件不超过 5MB）
                      </p>
                      <div
                        className={`file-upload-box ${idCardFile ? 'has-file' : ''} ${fileErrors.id_card ? 'has-error' : ''}`}
                        onClick={() => idCardInputRef.current?.click()}
                      >
                        {idCardFile ? (
                          <div className="file-info">
                            <i className="fas fa-file-alt file-icon"></i>
                            <div className="file-details">
                              <span className="file-name">{idCardFile.name}</span>
                              <span className="file-size">{(idCardFile.size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                            <button
                              type="button"
                              className="file-remove-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                setIdCardFile(null);
                                if (idCardInputRef.current) idCardInputRef.current.value = '';
                              }}
                              title="移除文件"
                            >
                              <i className="fas fa-times"></i>
                            </button>
                          </div>
                        ) : (
                          <div className="upload-placeholder">
                            <i className="fas fa-cloud-upload-alt fa-2x mb-2 text-muted"></i>
                            <span className="text-muted">点击上传居民身份证</span>
                            <span className="text-muted small">jpg / png / pdf ≤ 5MB</span>
                          </div>
                        )}
                      </div>
                      <input
                        ref={idCardInputRef}
                        type="file"
                        className="d-none"
                        accept=".jpg,.jpeg,.png,.pdf"
                        onChange={handleIdCardSelect}
                      />
                      {fileErrors.id_card && <div className="text-danger small mt-1">{fileErrors.id_card}</div>}
                    </div>

                    {/* b) 居住证明 */}
                    <div className="form-field mb-4">
                      <label className="form-label-lg">
                        <span className="field-number">b</span> 请上传您的居住证明
                        <span className="text-danger ms-1">*</span>
                      </label>
                      <p className="text-muted small mb-2">
                        点击上传您的居住证明（支持 jpg、png、pdf，单文件不超过 5MB）
                      </p>
                      <div
                        className={`file-upload-box ${housingProofFile ? 'has-file' : ''} ${fileErrors.housing_proof ? 'has-error' : ''}`}
                        onClick={() => housingProofInputRef.current?.click()}
                      >
                        {housingProofFile ? (
                          <div className="file-info">
                            <i className="fas fa-file-alt file-icon"></i>
                            <div className="file-details">
                              <span className="file-name">{housingProofFile.name}</span>
                              <span className="file-size">{(housingProofFile.size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                            <button
                              type="button"
                              className="file-remove-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                setHousingProofFile(null);
                                if (housingProofInputRef.current) housingProofInputRef.current.value = '';
                              }}
                              title="移除文件"
                            >
                              <i className="fas fa-times"></i>
                            </button>
                          </div>
                        ) : (
                          <div className="upload-placeholder">
                            <i className="fas fa-cloud-upload-alt fa-2x mb-2 text-muted"></i>
                            <span className="text-muted">点击上传居住证明</span>
                            <span className="text-muted small">jpg / png / pdf ≤ 5MB</span>
                          </div>
                        )}
                      </div>
                      <input
                        ref={housingProofInputRef}
                        type="file"
                        className="d-none"
                        accept=".jpg,.jpeg,.png,.pdf"
                        onChange={handleHousingProofSelect}
                      />
                      {fileErrors.housing_proof && <div className="text-danger small mt-1">{fileErrors.housing_proof}</div>}
                    </div>

                    {uploadError && (
                      <div className="alert alert-danger">
                        <i className="fas fa-exclamation-circle me-2"></i>{uploadError}
                      </div>
                    )}

                    <div className="form-actions d-flex gap-3">
                      <button
                        type="button"
                        className="btn btn-outline-secondary btn-lg"
                        onClick={() => setStep(1)}
                        disabled={uploading}
                      >
                        <i className="fas fa-arrow-left me-1"></i>上一步
                      </button>
                      <button
                        type="submit"
                        className="btn btn-submit btn-lg flex-grow-1"
                        disabled={uploading}
                      >
                        {uploading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            上传中...
                          </>
                        ) : (
                          <>
                            提交 <i className="fas fa-paper-plane ms-2"></i>
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* ===== 步骤3：成功页 ===== */}
            {step === 3 && (
              <div className="form-card">
                <div className="form-card-body">
                  <div className="success-page text-center py-5">
                    <div className="success-icon-wrapper mb-4">
                      <i className="fas fa-check-circle fa-6x text-success"></i>
                    </div>
                    <h3 className="success-title mb-3">申请提交成功！</h3>
                    <p className="success-desc mb-5">
                      请等待工作人员审核，通常 1–3 个工作日
                    </p>
                    <div className="success-actions d-flex justify-content-center gap-3 flex-wrap">
                      <Link to="/pets" className="btn btn-submit btn-lg px-4">
                        <i className="fas fa-arrow-left me-2"></i>返回
                      </Link>
                      <Link to="/my-applications" className="btn btn-submit btn-lg px-4">
                        <i className="fas fa-clipboard-list me-2"></i>查看申请详情
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ===== 样式 ===== */}
      <style>{`
        .adopt-application-page {
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

        /* 页面标题行 + 步骤指示器 */
        .page-header-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        .page-title {
          font-size: 1.4rem;
          font-weight: 600;
          color: #333;
        }
        .page-title strong {
          color: #00C897;
        }

        /* 步骤指示器 */
        .step-indicator {
          display: flex;
          align-items: center;
          gap: 0.4rem;
        }
        .step-dot {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #e9ecef;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
        }
        .step-dot-num {
          font-size: 0.8rem;
          font-weight: 700;
          color: #999;
        }
        .step-dot.active {
          background: #00C897;
        }
        .step-dot.active .step-dot-num {
          color: white;
        }
        .step-dot.completed {
          background: #28a745;
        }
        .step-dot.completed .step-dot-num {
          color: white;
        }
        .step-dot-label {
          font-size: 0.8rem;
          color: #999;
          white-space: nowrap;
        }
        .step-dot-label.active {
          color: #00C897;
          font-weight: 600;
        }
        .step-connector {
          width: 36px;
          height: 3px;
          background: #e9ecef;
          border-radius: 2px;
          margin: 0 0.25rem;
          transition: all 0.3s ease;
        }
        .step-connector.completed {
          background: #28a745;
        }

        /* 表单卡片 */
        .form-card {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        .form-card-header {
          background: linear-gradient(135deg, #00C897, #009B74);
          color: white;
          padding: 1.25rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .form-card-body {
          padding: 2rem;
        }

        /* 表单字段编号 */
        .form-label-lg {
          font-size: 1rem;
          font-weight: 600;
          color: #333;
          margin-bottom: 0.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .field-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 26px;
          height: 26px;
          border-radius: 50%;
          background: #00C897;
          color: white;
          font-size: 0.8rem;
          font-weight: 700;
          flex-shrink: 0;
        }

        /* 单选卡片组 */
        .radio-group {
          display: flex;
          flex-wrap: wrap;
          gap: 0.6rem;
        }
        .radio-card {
          position: relative;
          cursor: pointer;
          margin: 0;
        }
        .radio-card input[type="radio"] {
          position: absolute;
          opacity: 0;
          width: 0;
          height: 0;
        }
        .radio-card-label {
          display: inline-block;
          padding: 0.55rem 1.25rem;
          border: 2px solid #e0e0e0;
          border-radius: 25px;
          font-size: 0.9rem;
          color: #666;
          transition: all 0.2s ease;
          user-select: none;
        }
        .radio-card input[type="radio"]:checked + .radio-card-label {
          border-color: #00C897;
          background: #e9f7f2;
          color: #00A87A;
          font-weight: 600;
        }
        .radio-card:hover .radio-card-label {
          border-color: #00C897;
        }

        /* 多选卡片组 */
        .checkbox-group {
          display: flex;
          flex-wrap: wrap;
          gap: 0.6rem;
        }
        .checkbox-card {
          position: relative;
          cursor: pointer;
          margin: 0;
        }
        .checkbox-card input[type="checkbox"] {
          position: absolute;
          opacity: 0;
          width: 0;
          height: 0;
        }
        .checkbox-card-label {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          padding: 0.55rem 1.25rem;
          border: 2px solid #e0e0e0;
          border-radius: 25px;
          font-size: 0.9rem;
          color: #666;
          transition: all 0.2s ease;
          user-select: none;
        }
        .checkbox-card input[type="checkbox"]:checked + .checkbox-card-label {
          border-color: #00C897;
          background: #e9f7f2;
          color: #00A87A;
          font-weight: 600;
        }
        .checkbox-card input[type="checkbox"]:checked + .checkbox-card-label::before {
          content: '\\f00c';
          font-family: 'Font Awesome 5 Free';
          font-weight: 900;
          font-size: 0.75rem;
          color: #00C897;
        }
        .checkbox-card:hover .checkbox-card-label {
          border-color: #00C897;
        }

        /* 表单控件 */
        .form-control-lg, .form-select {
          border-radius: 10px;
          border: 2px solid #e9ecef;
          transition: all 0.2s ease;
          font-size: 0.95rem;
        }
        .form-control-lg:focus, .form-select:focus {
          border-color: #00C897;
          box-shadow: 0 0 0 0.2rem rgba(0, 200, 151, 0.15);
        }
        .form-control-lg::placeholder {
          color: #c0c0c0;
        }

        /* ===== 文件上传区域 ===== */
        .upload-intro {
          background: #e9f7f2;
          border-radius: 10px;
          padding: 0.75rem 1rem;
          color: #00A87A;
          font-size: 0.9rem;
        }

        .file-upload-box {
          border: 2px dashed #d0d0d0;
          border-radius: 12px;
          padding: 1.5rem;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: center;
        }
        .file-upload-box:hover {
          border-color: #00C897;
          background: #f8fffd;
        }
        .file-upload-box.has-file {
          border-style: solid;
          border-color: #00C897;
          background: #e9f7f2;
        }
        .file-upload-box.has-error {
          border-color: #dc3545;
          background: #fff5f5;
        }

        .upload-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
        }

        .file-info {
          display: flex;
          align-items: center;
          gap: 1rem;
          text-align: left;
        }
        .file-icon {
          font-size: 2rem;
          color: #00C897;
        }
        .file-details {
          display: flex;
          flex-direction: column;
          flex: 1;
        }
        .file-name {
          font-weight: 600;
          color: #333;
          word-break: break-all;
        }
        .file-size {
          font-size: 0.8rem;
          color: #999;
        }
        .file-remove-btn {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          border: none;
          background: #fee;
          color: #dc3545;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          flex-shrink: 0;
        }
        .file-remove-btn:hover {
          background: #dc3545;
          color: white;
        }

        /* 提交按钮 */
        .form-actions {
          margin-top: 2rem;
          padding-top: 1.5rem;
          border-top: 1px solid #eee;
        }
        .btn-submit {
          background: linear-gradient(135deg, #00C897, #00A87A);
          border: none;
          color: white;
          font-size: 1.1rem;
          font-weight: 600;
          padding: 0.9rem;
          border-radius: 30px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(0, 200, 151, 0.3);
          letter-spacing: 1px;
        }
        .btn-submit:hover:not(:disabled) {
          background: linear-gradient(135deg, #00B386, #00936A);
          transform: translateY(-3px);
          box-shadow: 0 8px 25px rgba(0, 200, 151, 0.4);
          color: white;
        }
        .btn-submit:active:not(:disabled) {
          transform: translateY(-1px);
        }
        .btn-submit:disabled {
          opacity: 0.7;
        }

        /* ===== 成功页 ===== */
        .success-icon-wrapper {
          animation: scaleIn 0.6s ease;
        }
        @keyframes scaleIn {
          0% { transform: scale(0); opacity: 0; }
          60% { transform: scale(1.2); }
          100% { transform: scale(1); opacity: 1; }
        }
        .success-title {
          font-size: 1.8rem;
          font-weight: 700;
          color: #222;
        }
        .success-desc {
          font-size: 1.05rem;
          color: #666;
        }

        /* 响应式 */
        @media (max-width: 768px) {
          .page-header-row {
            flex-direction: column;
            align-items: flex-start;
          }
          .form-card-body {
            padding: 1.25rem;
          }
          .success-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default AdoptApplication;
