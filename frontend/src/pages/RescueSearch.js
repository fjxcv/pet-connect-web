/**
 * @file RescueSearch.js
 * @module PawRescue
 * @description 页面组件：RescueSearch。
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { rescueAPI } from '../api/api';
import { RESCUE_STATUS } from '../constants/site';
const MAX_RECENT = 3;
const getUserId = () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    return user?.id || null;
  } catch {
    return null;
  }
};
const getRecentKey = () => {
  const uid = getUserId();
  return uid ? `pet_connect_recent_searches_${uid}` : 'pet_connect_recent_searches_anon';
};
const loadRecent = () => {
  try {
    return JSON.parse(localStorage.getItem(getRecentKey()) || '[]');
  } catch {
    return [];
  }
};
const saveRecent = (list) => {
  localStorage.setItem(getRecentKey(), JSON.stringify(list));
};
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
  const [recentSearches, setRecentSearches] = useState(loadRecent);
  // 每次 recentSearches 变化时同步到 localStorage
  useEffect(() => {
    saveRecent(recentSearches);
  }, [recentSearches]);
  const addToRecent = (value) => {
    setRecentSearches((prev) => {
      const filtered = prev.filter((v) => v !== value);
      return [value, ...filtered].slice(0, MAX_RECENT);
    });
  };
  const handleSearch = async (searchValue) => {
    const trimmed = (searchValue || keyword).trim();
    if (!trimmed) return;
    try {
      setSearching(true);
      setSearched(true);
      if (!searchValue) setKeyword(trimmed);
      const res = await rescueAPI.getAll({ rescue_no: trimmed });
      const list = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setResults(list);
      addToRecent(trimmed);
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
    <div className="d-flex flex-column" style={{ minHeight: 'calc(100vh - 160px)' }}>
      {/* 标题：左上角 */}
      <h2 className="mb-4">
        <i className="fas fa-search me-2 text-success"></i>救助查询
      </h2>
      {/* 搜索框 + 结果：居中 */}
      <div className="row justify-content-center">
        <div className="col-lg-5">
          {/* 查询区 */}
          <div className="input-group mb-3">
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
              onClick={() => handleSearch()}
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
          {/* 最近搜索：搜索框下方，默认保留位置 */}
          <div className="mb-3">
            <small className="text-muted d-block mb-2">
              <i className="fas fa-history me-1"></i>最近搜索
            </small>
            {recentSearches.length > 0 ? (
              <div className="d-flex flex-wrap gap-2">
                {recentSearches.map((no, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => {
                      setKeyword(no);
                      handleSearch(no);
                    }}
                  >
                    {no}
                  </button>
                ))}
              </div>
            ) : (
              <span className="text-muted" style={{ fontSize: '0.8rem' }}>暂无搜索记录</span>
            )}
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
        </div>
      </div>
      {/* 返回按钮：贴近白色区域底部 */}
      <div className="text-center mt-auto pt-4 pb-3">
        <button
          className="btn btn-outline-success"
          onClick={() => navigate('/rescue')}
        >
          <i className="fas fa-arrow-left me-1"></i>返回
        </button>
      </div>
    </div>
  );
};

export default RescueSearch;

