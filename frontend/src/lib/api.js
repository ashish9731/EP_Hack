import axios from 'axios';
import { getDeviceFingerprint } from './deviceFingerprint';

// Dynamically determine backend URL based on current domain
const API_URL = process.env.REACT_APP_BACKEND_URL || (typeof window !== 'undefined' ? window.location.origin.replace(':3000', ':5001') : '');

console.log('API URL:', API_URL); // Debug log

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store session token from login/signup responses
api.interceptors.response.use((response) => {
  console.log('API Response:', response); // Debug log
  if (response.data?.session_token) {
    localStorage.setItem('session_token', response.data.session_token);
  }
  return response;
}, (error) => {
  console.error('API Error:', error); // Debug log
  return Promise.reject(error);
});

// Add session token and device fingerprint to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('session_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Add device fingerprint
  const fingerprint = getDeviceFingerprint();
  config.headers['X-Device-Fingerprint'] = fingerprint;
  
  console.log('API Request:', config); // Debug log
  return config;
});

export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => {
    localStorage.removeItem('session_token');
    return api.post('/auth/logout');
  },
  getMe: () => api.get('/auth/me'),
  googleRedirect: () => {
    console.log('Calling googleRedirect API'); // Debug log
    return api.get('/auth/google-redirect');
  },
};

export const videoAPI = {
  upload: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (onProgress) onProgress(percentCompleted);
      },
    });
  },
  process: (videoId) => api.post(`/videos/${videoId}/process`),
  getJobStatus: (jobId) => api.get(`/jobs/${jobId}/status`),
};

export const reportAPI = {
  getReport: (reportId) => api.get(`/reports/${reportId}`),
  listReports: () => api.get('/reports'),
  createShareLink: (reportId) => api.post(`/reports/${reportId}/share`),
  getSharedReport: (shareId) => api.get(`/shared/reports/${shareId}`),
};

export const coachingAPI = {
  createRequest: (payload) => api.post('/coaching/requests', payload),
};


export const subscriptionAPI = {
  getStatus: () => api.get('/subscription/status'),
  upgrade: (tier, billingCycle) => api.post('/subscription/upgrade', { tier, billing_cycle: billingCycle }),
  checkVideoLimit: () => api.post('/subscription/check-video-limit'),
  incrementUsage: () => api.post('/subscription/increment-usage'),
};

export const retentionAPI = {
  getSettings: () => api.get('/retention/settings'),
  setDefaultRetention: (retention_period) => api.put('/retention/settings/default', { retention_period }),
  setVideoRetention: (videoId, retention_period) => api.put(`/retention/videos/${videoId}`, { retention_period }),
  deleteVideo: (videoId) => api.delete(`/retention/videos/${videoId}`),
};