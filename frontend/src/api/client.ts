import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

// Inject mock user header on every request
apiClient.interceptors.request.use((config) => {
  const stored = localStorage.getItem('lms_mock_user');
  if (stored) {
    config.headers['X-Mock-User'] = stored;
  }
  return config;
});

export default apiClient;
