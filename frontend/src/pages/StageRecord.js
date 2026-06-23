import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { rescueAPI } from '../api/api';

// 格式化时间为 "年.月.日 时:分"
const formatDateTime = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

const StageRecord = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState(null);
  const [records, setRecords] = useState([]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [validationError, setValidationError] = useState('');

  // 加载救助案例和已有记录
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [caseRes, recordsRes] = await Promise.all([
        rescueAPI.getById(id),
        rescueAPI.getStageRecords(id),
      ]);
      setCaseData(caseRes.data);
      setRecords(Array.isArray(recordsRes.data) ? recordsRes.data : []);
    } catch (err) {
      setError('加载数据失败，请稍后重试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 提交记录
  const handleSubmit = async () => {
    setValidationError('');

    if (!content.trim()) {
      setValidationError('请填写当前阶段的详细记录');
      return;
    }

    try {
      setSubmitting(true);
      const res = await rescueAPI.addStageRecord(id, { content: content.trim() });
      // 新增的记录加入列表顶部
      setRecords((prev) => [res.data, ...prev]);
      setContent('');
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail || '填写失败，请重试。';
      setValidationError(detail);
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // 返回我的救助页
  const handleBack = () => {
    navigate('/my-rescues');
  };

  // 加载中
  if (loading) {
    return (
      <div className="py-3 text-center">
        <div className="spinner-border text-success" role="status"></div>
        <p className="mt-2 text-muted">加载中...</p>
      </div>
    );
  }

  // 加载失败
  if (error) {
    return (
      <div className="py-3">
        <div className="alert alert-danger d-flex align-items-center gap-2">
          <i className="fas fa-exclamation-triangle"></i>
          <span>{error}</span>
          <button className="btn btn-outline-danger btn-sm ms-auto" onClick={fetchData}>
            重试
          </button>
        </div>
        <div className="text-center mt-3">
          <button className="btn btn-outline-success" onClick={handleBack}>
            <i className="fas fa-arrow-left me-1"></i>返回
          </button>
        </div>
      </div>
    );
  }

  // 填写成功提示
  if (success) {
    return (
      <div className="py-3">
        <div className="row">
          <div className="col-lg-6 mx-auto">
            <div className="text-center py-5">
              <i className="fas fa-check-circle fa-4x text-success mb-3 d-block"></i>
              <h4 className="mb-3">填写成功</h4>
              <p className="text-muted mb-4">
                救助编号 <strong>{caseData?.rescue_no}</strong> 的阶段记录已保存。
              </p>
              <button className="btn btn-success" onClick={handleBack}>
                <i className="fas fa-arrow-left me-1"></i>返回
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-3">
      <div className="row">
        <div className="col-lg-8 mx-auto">
          {/* 标题 */}
          <h2 className="mb-4">
            <i className="fas fa-clipboard-list me-2 text-success"></i>填写记录
          </h2>

          {/* 救助编号 */}
          <div className="mb-3">
            <span className="text-muted">救助编号：</span>
            <span className="fw-bold">{caseData?.rescue_no}</span>
          </div>

          {/* 输入区域 */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label fw-bold">
                  当前阶段记录 <span className="text-danger">*</span>
                </label>
                <textarea
                  className="form-control"
                  rows={5}
                  placeholder="请填写当前阶段的详细记录..."
                  value={content}
                  onChange={(e) => {
                    setContent(e.target.value);
                    setValidationError('');
                    setSuccess(false);
                  }}
                  disabled={submitting}
                ></textarea>
              </div>

              {/* 校验错误 */}
              {validationError && (
                <div className="alert alert-danger py-2 mb-3">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {validationError}
                </div>
              )}

              {/* 操作按钮 */}
              <div className="d-flex justify-content-center gap-2">
                <button
                  className="btn btn-success"
                  type="button"
                  onClick={handleSubmit}
                  disabled={submitting || !content.trim()}
                >
                  {submitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                      提交中...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-paper-plane me-1"></i>提交记录
                    </>
                  )}
                </button>
                <button
                  className="btn btn-outline-secondary"
                  type="button"
                  onClick={handleBack}
                  disabled={submitting}
                >
                  <i className="fas fa-arrow-left me-1"></i>返回
                </button>
              </div>
            </div>
          </div>

          {/* 历史记录列表 */}
          {records.length > 0 && (
            <div className="card">
              <div className="card-header">
                <i className="fas fa-history me-2"></i>
                历史记录（共 {records.length} 条）
              </div>
              <div className="list-group list-group-flush">
                {records.map((record) => (
                  <div key={record.id} className="list-group-item">
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <small className="text-muted">
                        <i className="far fa-clock me-1"></i>
                        {formatDateTime(record.created_at)}
                      </small>
                      {record.operator && (
                        <small className="text-muted">
                          <i className="fas fa-user me-1"></i>
                          {record.operator.username}
                        </small>
                      )}
                    </div>
                    <p className="mb-0" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {record.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StageRecord;
