import Axios from 'axios';
import { message } from 'antd';

const apiClient = Axios.create();

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = token;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      message.error('Session ist abgelaufen');
      window.dispatchEvent(new CustomEvent('plainbi:unauthorized'));
    }
    return Promise.reject(error);
  }
);

export default apiClient;
