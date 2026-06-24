import api from './index';

export const authAPI = {
  login: (credentials) => api.post('/token/', credentials),
  register: (userData) => api.post('/register/', userData),
<<<<<<< HEAD
  requestRegisterCode: (payload) => api.post('/auth/email/register-request/', payload),
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  getProfile: () => api.get('/profile/'),
  updateProfile: (userData) => api.put('/profile/', userData),
  passwordResetRequest: (email) => api.post('/auth/password/reset-request/', { email }),
  passwordResetConfirm: (data) => api.post('/auth/password/reset-confirm/', data),
  emailChangeRequest: (new_email) => api.post('/auth/email/change-request/', { new_email }),
  emailChangeConfirm: (data) => api.post('/auth/email/change-confirm/', data),
};
