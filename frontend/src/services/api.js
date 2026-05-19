import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw new Error('An error occurred while communicating with the server');
  }
);

export const chatService = {
  async sendMessage(query) {
    try {
      const response = await api.post('/chat', { query });
      return response.data;
    } catch (error) {
      console.error('Chat Service Error:', error);
      throw error;
    }
  },

  async checkHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health Check Error:', error);
      throw error;
    }
  }
};

export default api;
