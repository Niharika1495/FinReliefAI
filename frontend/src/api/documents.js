import api from './axios';

export const documentsApi = {
  upload: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },
  getDocuments: () => api.get('/documents'),
};
