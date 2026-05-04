import api from '../api/axios';

export const DataService = {
  getAll: async () => {
    const response = await api.get('/items'); 
    return response.data;
  }
};