/**
 * @file modules.js
 * @module PawRescue
 * @description REST API 模块化封装。
 */

import api from './index';


/** 门户首页：轮播图与统计数据 */
export const portalAPI = {
  getCarousel: () => api.get('/portal/carousel/'),
  createCarousel: (data) => api.post('/portal/carousel/', data),
  updateCarousel: (id, data) => api.patch(`/portal/carousel/${id}/`, data),
  deleteCarousel: (id) => api.delete(`/portal/carousel/${id}/`),
  getStats: () => api.get('/portal/stats/'),
  getDashboard: () => api.get('/portal/dashboard/'),
};


/** CMS 内容：文章、收藏与公告 */
export const cmsAPI = {
  getCategories: () => api.get('/cms/categories/'),
  getArticles: (params) => api.get('/cms/articles/', { params }),
  getArticle: (id) => api.get(`/cms/articles/${id}/`),
  createArticle: (data) => api.post('/cms/articles/', data),
  updateArticle: (id, data) => api.patch(`/cms/articles/${id}/`, data),
  deleteArticle: (id) => api.delete(`/cms/articles/${id}/`),
  getFavorites: () => api.get('/cms/favorites/'),
  favoriteArticle: (id) => api.post(`/cms/articles/${id}/favorite/`),
  unfavoriteArticle: (id) => api.delete(`/cms/articles/${id}/favorite/`),
  getAnnouncements: () => api.get('/cms/announcements/'),
};


/** 用户公开主页与屏蔽 */
export const usersAPI = {
  getPublicProfile: (id) => api.get(`/users/${id}/public/`),
  blockUser: (id) => api.post(`/users/${id}/block/`),
  unblockUser: (id) => api.delete(`/users/${id}/block/`),
};


/** 寻宠资助帖 */
export const lostFoundAPI = {
  getAll: (params) => api.get('/lost-found/', { params }),
  getById: (id) => api.get(`/lost-found/${id}/`),
  create: (data) => api.post('/lost-found/', data),
  update: (id, data) => api.patch(`/lost-found/${id}/`, data),
  getNearby: (params) => api.get('/lost-found/nearby/', { params }),
  getMyPosts: () => api.get('/lost-found/my_posts/'),
};


/** 社区动态与互动 */
export const communityAPI = {
  getPosts: (params) => api.get('/community/posts/', { params }),
  getPost: (id) => api.get(`/community/posts/${id}/`),
  createPost: (data) => api.post('/community/posts/', data),
  updatePost: (id, data) => api.patch(`/community/posts/${id}/`, data),
  deletePost: (id) => api.delete(`/community/posts/${id}/`),
  getComments: (id) => api.get(`/community/posts/${id}/comments/`),
  addComment: (id, data) => api.post(`/community/posts/${id}/comments/`, data),
  deleteComment: (id) => api.delete(`/community/comments/${id}/`),
  likePost: (id) => api.post(`/community/posts/${id}/like/`),
  unlikePost: (id) => api.delete(`/community/posts/${id}/like/`),
  favoritePost: (id) => api.post(`/community/posts/${id}/favorite/`),
  unfavoritePost: (id) => api.delete(`/community/posts/${id}/favorite/`),
  getFavorites: () => api.get('/community/favorites/'),
  likeComment: (id) => api.post(`/community/comments/${id}/like/`),
  unlikeComment: (id) => api.delete(`/community/comments/${id}/like/`),
};


/** 后台管理：看板、审核、配置与 AI 日志 */
/** 后台管理：看板、审核、配置与 AI 日志。【权限】仅 admin */
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard/'),
  getUsers: (params) => api.get('/admin/users/', { params }),
  updateUser: (id, data) => api.patch(`/admin/users/${id}/`, data),
  getModeration: () => api.get('/admin/moderation/'),
  createModeration: (data) => api.post('/admin/moderation/', data),
  getConfig: () => api.get('/admin/config/'),
  updateConfig: (key, data) => api.patch(`/admin/config/${key}/`, data),
  getAiLogs: (params) => api.get('/admin/ai-logs/', { params }),
  getAiLogStats: () => api.get('/admin/ai-logs/stats/'),
};
const AI_TIMEOUT_MS = 90000;


/** AI 辅助。【权限】user/admin 需登录 */
export const aiAPI = {
  breedDetect: (data) => api.post('/ai/breed-detect/', data, { timeout: AI_TIMEOUT_MS }),
  adoptCopy: (data) => api.post('/ai/adopt-copy/', data, { timeout: AI_TIMEOUT_MS }),
  qa: (data) => api.post('/ai/qa/', data, { timeout: AI_TIMEOUT_MS }),
};

