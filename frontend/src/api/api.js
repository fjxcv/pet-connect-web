/**
 * @file api.js
 * @module PawRescue
 * @description API 封装：api。
 */

export { default } from './index';

export { authAPI } from './auth';

export { petsAPI, rescueAPI, uploadAPI } from './pets';

export { adoptAPI } from './adopt';

export {
  portalAPI,
  cmsAPI,
  lostFoundAPI,
  communityAPI,
  adminAPI,
  aiAPI,
  usersAPI,
} from './modules';

