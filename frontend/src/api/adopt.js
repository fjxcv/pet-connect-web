/**
 * @file adopt.js
 * @module PawRescue
 * @description API 封装：adopt。
 */

import api from './index';

export const adoptAPI = {
  getAll: () => api.get('/adopt/applications/admin/'),
  getAllLegacy: () => api.get('/adopt/applications/'),
  getById: (id) => api.get(`/adopt/applications/${id}/`),
  create: (data) => api.post('/adopt/applications/', data),
  getMy: () => api.get('/adopt/applications/my/'),
  submitQuestionnaire: (id, answers_json) => api.post(`/adopt/applications/${id}/questionnaire/`, { answers_json }),
  addAttachment: (id, data) => api.post(`/adopt/applications/${id}/attachments/`, data),
  audit: (id, data) => api.put(`/adopt/applications/${id}/audit/`, data),
  getReviewDetail: (id) => api.get(`/adopt/applications/${id}/review-detail/`),
  offlineVerify: (id, data) => api.put(`/adopt/offline-verify/${id}/`, data),
};

