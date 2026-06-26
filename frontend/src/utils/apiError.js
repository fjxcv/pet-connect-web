/**
 * @file apiError.js
 * @module PawRescue
 * @description 工具函数：apiError。
 */

/**
 * Format DRF / axios error payload for display.
 */

export function formatApiError(err, fallback = '操作失败，请稍后重试。') {
  if (!err?.response?.data) {
    return err?.message || fallback;
  }
  const data = err.response.data;
  if (typeof data.detail === 'string') {
    return data.detail;
  }
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => (typeof item === 'string' ? item : JSON.stringify(item))).join('；');
  }
  const fieldMessages = Object.entries(data)
    .filter(([key]) => key !== 'detail')
    .map(([key, val]) => {
      const msg = Array.isArray(val) ? val[0] : val;
      return `${key}: ${msg}`;
    });
  if (fieldMessages.length) {
    return fieldMessages.join('；');
  }
  return fallback;
}

export function roundCoordinate(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  return Math.round(n * 1e6) / 1e6;
}

