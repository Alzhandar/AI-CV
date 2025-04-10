import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const authService = {
  register: (userData) => api.post('/auth/register/', userData),
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (userData) => api.put('/auth/profile/', userData),
};

const resumeService = {
  getAll: () => api.get('/resumes/'),
  get: (id) => api.get(`/resumes/${id}/`),
  create: (formData) => {
    return api.post('/resumes/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  update: (id, data) => api.put(`/resumes/${id}/`, data),
  delete: (id) => api.delete(`/resumes/${id}/`),
  analyze: (id) => api.post(`/resumes/${id}/analyze/`),
  getAnalysisResults: (id) => api.get(`/resumes/${id}/analysis_results/`),
};

const jobService = {
  getAll: () => api.get('/jobs/'),
  get: (id) => api.get(`/jobs/${id}/`),
  create: (data) => api.post('/jobs/', data),
  update: (id, data) => api.put(`/jobs/${id}/`, data),
  delete: (id) => api.delete(`/jobs/${id}/`),
  getMatching: () => api.get('/jobs/matching/'),
  matchResume: (jobId, resumeId) => api.get(`/jobs/${jobId}/match_resume/?resume_id=${resumeId}`),
};

const companyService = {
  getAll: () => api.get('/companies/'),
  get: (id) => api.get(`/companies/${id}/`),
  create: (data) => api.post('/companies/', data),
  update: (id, data) => api.put(`/companies/${id}/`, data),
  delete: (id) => api.delete(`/companies/${id}/`),
};

const skillService = {
  getAll: () => api.get('/skills/'),
};

const analysisService = {
  getAll: () => api.get('/analysis/'),
  get: (id) => api.get(`/analysis/${id}/`),
  getStatistics: () => api.get('/analysis/statistics/'),
};

export {
  api,
  authService,
  resumeService,
  jobService,
  companyService,
  skillService,
  analysisService,
};