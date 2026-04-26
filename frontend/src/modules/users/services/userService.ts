import api from '@/lib/api';

export const userService = {
  async getAll(params: any = {}) {
    const { data } = await api.get('/api/v1/users', { params });
    return data;
  },

  async getById(id: string) {
    const { data } = await api.get(`/api/v1/users/${id}`);
    return data;
  },

  async create(payload: any) {
    const { data } = await api.post('/api/v1/users', payload);
    return data;
  },

  async update(id: string, payload: any) {
    const { data } = await api.put(`/api/v1/users/${id}`, payload);
    return data;
  },

  async deactivate(id: string) {
    const { data } = await api.delete(`/api/v1/users/${id}`);
    return data;
  }
};
