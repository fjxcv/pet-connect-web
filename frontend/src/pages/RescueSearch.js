import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rescueAPI } from '../api/api';
import { RESCUE_STATUS } from '../constants/site';

const STATUS_COLOR = {
  pending_rescue: 'secondary',
  in_medical: 'warning',
  recovering: 'info',
  awaiting_adoption: 'primary',
  rescued: 'success',
  abandoned: 'dark',
};

const RescueSearch = () => {
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState(null); // null=未搜索, [] = 无结果
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    const trimmed = keyword.trim();
    if (!trimmed) return;

    try {
      setSearching(true);
      setSearched(true);
      const res = await rescueAPI.getAll({ rescue_no: trimmed });
      const list = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setResults(list);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div className="py-3">
      <div className="row">
        <div className="col-lg-6 mx-auto">
          <h2 className="mb-4">
            <i className="fas fa-search me-2 text-success"></i>救助查询
          </h2>

          {/* 查询区 */}
          <div className="input-group mb-4">
            <input
              type="text"
              className="form-control"
              placeholder="请输入救助编号"
              value={keyword}
              onChange={(e) => {
                setKeyword(e.target.value);
                setSearched(false);
              }}
              onKeyDown={handleKeyDown}
            />
            <button
              className="btn btn-success"
              type="button"
              onClick={handleSearch}
              disabled={searching || !keyword.trim()}
            >
              {searching ? (
                <>
                  <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                  查询中...
                </>
              ) : (
                <>
                  <i className="fas fa-search me-1"></i>查询
                </>
              )}
            </button>
          </div>

          {/* 结果区 */}
          {searched && (
            results === null || searching ? null : results.length > 0 ? (
              <div className="list-group">
                {results.map((item) => (
                  <button
                    key={item.id}
                    className="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-3"
                    type="button"
                    onClick={() => navigate(`/rescue/${item.id}`)}
                  >
                    <span className="fw-bold fs-6">{item.rescue_no}</span>
                    <span className={`badge bg-${STATUS_COLOR[item.current_status] || 'secondary'} fs-6`}>
                      {RESCUE_STATUS[item.current_status] || item.current_status}
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-center py-4">
                <i className="fas fa-search fa-2x text-muted mb-2 d-block"></i>
                <p className="text-muted">未找到该救助编号</p>
              </div>
            )
          )}

          {/* 返回按钮 */}
          <div className="text-center mt-5 pt-2">
            <button
              className="btn btn-outline-success"
              onClick={() => navigate('/rescue')}
            >
              <i className="fas fa-arrow-left me-1"></i>返回
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RescueSearch;
