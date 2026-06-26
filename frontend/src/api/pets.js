/**
 * @file pets.js
 * @module PawRescue
 * @description API 封装：pets。
 */

import api from './index';

export const uploadAPI = {
  upload: (file, subdir = 'uploads') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subdir', subdir);
    return api.post('/uploads/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const petsAPI = {
  getAll: (params) => api.get('/pets/', { params }),
  getNearby: (params) => api.get('/pets/nearby/', { params }),
  getById: (id) => api.get(`/pets/${id}/`),
  create: (data) => api.post('/pets/', data),
  update: (id, data) => api.patch(`/pets/${id}/`, data),
  delete: (id) => api.delete(`/pets/${id}/`),
  getMyPets: () => api.get('/pets/my/'),
};

export const rescueAPI = {
  getAll: (params) => api.get('/rescue/cases/', { params }),
  getById: (id) => api.get(`/rescue/cases/${id}/`),
  getMyCases: () => api.get('/rescue/cases/', { params: { my: 'true', exclude_status: 'awaiting_adoption' } }),
  getHelpedCases: (params) => api.get('/rescue/cases/', { params: { helped: 'true', ...params } }),
  create: (data) => api.post('/rescue/cases/', data),
  help: (id) => api.post(`/rescue/cases/${id}/help/`),
  updateStatus: (id, data) => api.patch(`/rescue/cases/${id}/status/`, data),
  getStageRecords: (id) => api.get(`/rescue/cases/${id}/stage-records/`),
  addStageRecord: (id, data) => api.post(`/rescue/cases/${id}/stage-records/`, data),
};

