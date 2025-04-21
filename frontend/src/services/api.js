import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Важно для отправки и получения кук
});

// Функция для получения CSRF токена из куки
function getCsrfToken() {
  const name = 'csrftoken';
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
  }
  return null;
}

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // Добавляем CSRF-токен для не GET запросов
    if (config.method !== 'get') {
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);


const authService = {
  // Исправляем пути API для соответствия бэкенду
  register: (userData) => {
    // Преобразуем confirmPassword в password_confirm
    if (userData.confirmPassword !== undefined) {
      userData = {...userData, password_confirm: userData.confirmPassword};
      delete userData.confirmPassword;
    }
    console.log("Данные регистрации:", userData);
    return api.post('/auth/register/', userData);
  },
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/profile/'), // Исправлено с auth/profile/ на profile/
  updateProfile: (userData) => api.put('/profile/', userData), // Исправлено с auth/profile/ на profile/
};

const resumeService = {
  getAll: () => api.get('/resumes/resumes/'),
  get: (id) => api.get(`/resumes/resumes/${id}/`),
  create: (formData) => {
    return api.post('/resumes/resumes/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  update: (id, data) => api.put(`/resumes/resumes/${id}/`, data),
  delete: (id) => api.delete(`/resumes/resumes/${id}/`),
  analyze: (id) => api.post(`/resumes/resumes/${id}/reanalyze/`),
  getAnalysisResults: (id) => api.get(`/resumes/resumes/${id}/analysis/`),
  getMatchingJobs: (id) => api.get(`/resumes/resumes/${id}/matching_jobs/`),
  gptAnalyze: (id) => api.post(`/resumes/resumes/${id}/gpt_analyze/`),
};

const jobService = {
  getAll: () => api.get('/jobs/job-listings/'),
  get: (identifier) => api.get(`/jobs/job-listings/${identifier}/`),
  create: (data) => api.post('/jobs/job-listings/', data),
  update: (id, data) => api.put(`/jobs/job-listings/${id}/`, data),
  delete: (id) => api.delete(`/jobs/job-listings/${id}/`),
  getMatching: () => api.get('/jobs/matching/'),
  matchResume: (jobId, resumeId) => api.get(`/jobs/job-listings/${jobId}/match_resume/?resume_id=${resumeId}`),
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