import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { communityAPI } from '../api/api';
import { uploadAPI } from '../api/pets';
import { POST_CATEGORIES } from '../constants/site';

const CATEGORY_OPTIONS = Object.entries(POST_CATEGORIES).map(([value, label]) => ({ value, label }));
const MAX_IMAGES = 9;
const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp'];

const CommunityPublish = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [form, setForm] = useState({ category: 'general', title: '', content: '' });
  const [imageItems, setImageItems] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    return () => {
      imageItems.forEach((item) => URL.revokeObjectURL(item.preview));
    };
  }, [imageItems]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validateImageFile = (file) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !ALLOWED_IMAGE_EXTENSIONS.includes(ext)) {
      return `仅支持 JPG/PNG/WEBP 格式，当前文件: ${file.name}`;
    }
    if (file.size > MAX_IMAGE_SIZE) {
      return `单张图片不能超过 5MB，当前文件: ${file.name}`;
    }
    return '';
  };

  const uploadFiles = async (files) => {
    const selected = Array.from(files);
    if (!selected.length) return;

    if (imageItems.length + selected.length > MAX_IMAGES) {
      setUploadError(`最多只能上传 ${MAX_IMAGES} 张图片`);
      return;
    }

    setUploadError('');
    setUploading(true);

    try {
      for (const file of selected) {
        const invalidMessage = validateImageFile(file);
        if (invalidMessage) {
          setUploadError(invalidMessage);
          continue;
        }

        const preview = URL.createObjectURL(file);
        const response = await uploadAPI.upload(file, 'community');
        setImageItems((prev) => [
          ...prev,
          { file, preview, url: response.data.url },
        ]);
      }
    } catch (err) {
      console.error(err);
      setUploadError('图片上传失败，请检查网络后重试。');
    } finally {
      setUploading(false);
    }
  };

  const handleFileInputChange = async (e) => {
    await uploadFiles(e.target.files);
    e.target.value = '';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length) {
      await uploadFiles(e.dataTransfer.files);
    }
  };

  const handleRemoveImage = (index) => {
    setImageItems((prev) => {
      const next = [...prev];
      const [removed] = next.splice(index, 1);
      if (removed?.preview) {
        URL.revokeObjectURL(removed.preview);
      }
      return next;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const payload = {
        ...form,
        image_urls: imageItems.map((item) => item.url),
      };
      const res = await communityAPI.createPost(payload);
      navigate(`/community/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || '发帖失败，请重试。');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="py-3">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/community">社区交流</Link></li>
          <li className="breadcrumb-item active">发帖</li>
        </ol>
      </nav>

      <h2 className="mb-4"><i className="fas fa-pen me-2 text-success"></i>发布帖子</h2>

      {error && <div className="alert alert-danger">{error}</div>}
      {uploadError && <div className="alert alert-warning">{uploadError}</div>}

      <form onSubmit={handleSubmit} className="card shadow-sm">
        <div className="card-body">
          <div className="mb-3">
            <label className="form-label">分类</label>
            <select name="category" className="form-select" value={form.category} onChange={handleChange} required>
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div className="mb-3">
            <label className="form-label">标题</label>
            <input
              type="text"
              name="title"
              className="form-control"
              value={form.title}
              onChange={handleChange}
              required
              maxLength={200}
              placeholder="请输入帖子标题"
            />
          </div>
          <div className="mb-3">
            <label className="form-label">内容</label>
            <textarea
              name="content"
              className="form-control"
              rows={8}
              value={form.content}
              onChange={handleChange}
              required
              placeholder="请输入帖子内容"
            />
          </div>
          <div
            className={`upload-drop-zone mb-3 ${dragActive ? 'upload-drop-zone--active' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
          >
            <div className="upload-drop-zone__content">
              <h5 className="upload-drop-zone__title">图片上传（最多 9 张）</h5>
              <p className="upload-drop-zone__hint">
                仅支持 PC 端本地图片选择和拖拽上传。仅允许 JPG / PNG / WEBP，单张不超过 5MB。
              </p>
              <button
                type="button"
                className="btn upload-select-button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading || submitting}
              >
                选择图片
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              className="upload-file-input"
              accept="image/*"
              multiple
              onChange={handleFileInputChange}
              disabled={uploading || submitting}
            />
          </div>

          {imageItems.length > 0 && (
            <div className="mb-3">
              <div className="row g-2">
                {imageItems.map((item, index) => (
                  <div className="col-6 col-sm-4 col-md-3" key={`${item.url}-${index}`}>
                    <div className="position-relative border rounded overflow-hidden" style={{ minHeight: 120 }}>
                      <img
                        src={item.preview}
                        alt={`preview-${index}`}
                        className="w-100 h-100"
                        style={{ objectFit: 'cover', minHeight: 120 }}
                      />
                      <button
                        type="button"
                        className="btn btn-sm btn-danger position-absolute top-0 end-0 m-1"
                        onClick={() => handleRemoveImage(index)}
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="card-footer d-flex justify-content-center gap-2 flex-wrap">
          <button type="submit" className="btn btn-success" disabled={submitting || uploading}>
            {submitting ? '发布中...' : '发布'}
          </button>
          <Link to="/community" className="btn btn-outline-secondary">取消</Link>
          {(uploading || submitting) && <span className="align-self-center text-muted">请等待上传完成后再提交。</span>}
        </div>
      </form>
    </div>
  );
};

export default CommunityPublish;
