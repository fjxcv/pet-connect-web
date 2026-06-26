/**
 * @file BreedDetectResult.js
 * @module PawRescue
 * @description 可复用组件：BreedDetectResult。
 */

import React from 'react';
/**
 * 功能：展示 AI 品种识别结果。
 * 【权限】由 AddPet 等页面在登录后调用。
 */
const BreedDetectResult = ({ data, className = '' }) => {
  if (!data) return null;
  const {
    species,
    breed,
    summary,
    result,
    confidence,
    breed_candidates: candidates,
    low_confidence: lowConfidence,
  } = data;
  const list = Array.isArray(candidates) && candidates.length > 0
    ? candidates
    : (breed && breed !== '不确定' ? [{ breed, confidence: confidence ?? 0.85 }] : []);
  const hasStructured = Boolean(
    (species && species !== '不确定')
    || list.length > 0
    || (summary && summary !== '不确定' && summary !== '无'),
  );
  const showResultFallback = Boolean(result) && !hasStructured;
  if (!hasStructured && !showResultFallback) return null;
  return (
    <div className={`breed-detect-result ${className}`.trim()}>
      {species && species !== '不确定' && (
        <div className="mb-2 small">
          <span className="text-muted">物种</span>
          <span className="ms-2 fw-semibold">{species}</span>
        </div>
      )}
      {list.length > 0 && (
        <div className="mb-2">
          <div className="text-muted small mb-1">候选品种</div>
          <ul className="list-unstyled mb-0 small">
            {list.map((item, idx) => {
              const pct = Math.round(Number(item.confidence || 0) * 100);
              return (
                <li key={`${item.breed}-${idx}`} className="mb-2">
                  <div className="d-flex justify-content-between align-items-center gap-2">
                    <span>
                      {idx === 0 && <span className="badge bg-success me-1">推荐</span>}
                      {item.breed}
                    </span>
                    <span className="text-muted">{pct}%</span>
                  </div>
                  <div className="progress mt-1" style={{ height: 6 }}>
                    <div
                      className="progress-bar bg-success"
                      role="progressbar"
                      style={{ width: `${Math.min(100, pct)}%` }}
                      aria-valuenow={pct}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
      {summary && summary !== '不确定' && summary !== '无' && (
        <div className="small text-muted">
          <span>备注</span>
          <span className="ms-2">{summary}</span>
        </div>
      )}
      {lowConfidence && (
        <p className="mb-0 mt-2 small text-muted">
          识别置信度较低，以上为参考品种，建议结合现场特征判断。
        </p>
      )}
      {showResultFallback && <p className="mb-0 small">{result}</p>}
    </div>
  );
};

export default BreedDetectResult;

