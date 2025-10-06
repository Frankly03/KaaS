import axios from 'axios';

// The backend URL will be proxied by Vite's dev server.
const API_URL = '/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const postQuery = (question, filename = null, k = 7) => {
  return apiClient.post('/query', { question, filename, k });
};

export const listDocuments = () => {
  return apiClient.get('/documents');
};


export const resetAllData = () => {
  return apiClient.post('/reset');
};
