/**
 * @file index.js
 * @module PawRescue
 * @description API 封装：index。
 */

import axios from 'axios';
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

