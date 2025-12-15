import axios from 'axios';
import { getDeviceFingerprint } from './deviceFingerprint';

// Dynamically determine backend URL based on current domain
const API_URL = process.env.REACT_APP_BACKEND_URL || (typeof window !== 'undefined' ? window.location.origin : '');

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store session token from login/signup responses
api.interceptors.response.use((response) => {
  if (response.data?.session_token) {
    localStorage.setItem('session_token', response.data.session_token);
  }
  return response;
}, (error) => {
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
  
  return config;
});

export const authAPI = {
  signup: (data) => Promise.resolve({
    data: {
      user: {
        user_id: "mock_user_123",
        email: data.email,
        name: data.name,
        created_at: new Date().toISOString()
      },
      session_token: "mock_session_token"
    }
  }),
  login: (data) => Promise.resolve({
    data: {
      user: {
        user_id: "mock_user_123",
        email: data.email,
        name: "Demo User",
        created_at: new Date().toISOString()
      },
      session_token: "mock_session_token"
    }
  }),
  logout: () => {
    localStorage.removeItem('session_token');
    return Promise.resolve({ data: { message: 'Logged out successfully' } });
  },
  getMe: () => Promise.resolve({
    data: {
      user_id: "mock_user_123",
      email: "demo@example.com",
      name: "Demo User",
      created_at: new Date().toISOString()
    }
  }),
  googleRedirect: () => Promise.resolve({
    data: {
      auth_url: "/dashboard"
    }
  }),
};

export const videoAPI = {
  upload: (file, onProgress) => {
    // Simulate upload progress
    if (onProgress) {
      setTimeout(() => onProgress(50), 100);
      setTimeout(() => onProgress(100), 200);
    }
    
    return Promise.resolve({
      data: {
        video_id: "mock_video_123",
        message: "Video uploaded successfully"
      }
    });
  },
  process: (videoId) => Promise.resolve({
    data: {
      job_id: "mock_job_123",
      message: "Processing started"
    }
  }),
  getJobStatus: (jobId) => Promise.resolve({
    data: {
      status: "completed",
      progress: 100,
      report_id: "mock_report_123"
    }
  }),
};

export const reportAPI = {
  getReport: (reportId) => Promise.resolve({
    data: {
      id: reportId,
      created_at: new Date().toISOString(),
      overall_score: 75,
      gravitas_score: 70,
      communication_score: 80,
      presence_score: 75,
      storytelling_score: 70,
      video_duration: 180,
      title: "Mock Report",
      transcription: "This is a mock transcription of the video.",
      feedback: {
        gravitas: "Good gravitas shown in the video.",
        communication: "Clear communication throughout.",
        presence: "Strong presence demonstrated.",
        storytelling: "Effective storytelling techniques used."
      }
    }
  }),
  listReports: () => Promise.resolve({
    data: {
      reports: [
        {
          id: "report_1",
          created_at: new Date().toISOString(),
          overall_score: 75,
          gravitas_score: 70,
          communication_score: 80,
          presence_score: 75,
          storytelling_score: 70,
          video_duration: 180,
          title: "Initial Assessment"
        }
      ]
    }
  }),
  createShareLink: (reportId) => Promise.resolve({
    data: {
      share_url: `https://example.com/shared/${reportId}`
    }
  }),
  getSharedReport: (shareId) => Promise.resolve({
    data: {
      id: "shared_report_1",
      created_at: new Date().toISOString(),
      overall_score: 75,
      gravitas_score: 70,
      communication_score: 80,
      presence_score: 75,
      storytelling_score: 70,
      video_duration: 180,
      title: "Shared Mock Report",
      transcription: "This is a mock transcription of the shared video.",
      feedback: {
        gravitas: "Good gravitas shown in the video.",
        communication: "Clear communication throughout.",
        presence: "Strong presence demonstrated.",
        storytelling: "Effective storytelling techniques used."
      }
    }
  }),
};

export const coachingAPI = {
  createRequest: (payload) => Promise.resolve({
    data: {
      message: "Coaching request submitted successfully",
      request_id: "mock_request_123"
    }
  }),
};


export const subscriptionAPI = {
  getStatus: () => Promise.resolve({
    data: {
      tier: "premium",
      status: "active",
      video_limit: 100,
      videos_used: 1,
      is_whitelisted: true
    }
  }),
  upgrade: (tier, billingCycle) => Promise.resolve({
    data: {
      message: "Subscription upgraded successfully"
    }
  }),
  checkVideoLimit: () => Promise.resolve({
    data: {
      can_upload: true,
      remaining_videos: 99
    }
  }),
  incrementUsage: () => Promise.resolve({
    data: {
      message: "Usage incremented successfully"
    }
  }),
};

export const retentionAPI = {
  getSettings: () => Promise.resolve({
    data: {
      default_retention_period: 30,
      video_retention_periods: {}
    }
  }),
  setDefaultRetention: (retention_period) => Promise.resolve({
    data: {
      message: "Default retention period updated successfully"
    }
  }),
  setVideoRetention: (videoId, retention_period) => Promise.resolve({
    data: {
      message: "Video retention period updated successfully"
    }
  }),
  deleteVideo: (videoId) => Promise.resolve({
    data: {
      message: "Video deleted successfully"
    }
  }),
};
