import api from '@/lib/api';

export const deliveryService = {
  async getAll(params: any = {}) {
    const { data } = await api.get('/api/v1/deliveries', { params });
    return data;
  },

  async getById(id: string) {
    const { data } = await api.get(`/api/v1/deliveries/${id}`);
    return data;
  },

  async create(payload: any) {
    const { data } = await api.post('/api/v1/deliveries', payload);
    return data;
  },

  async updateStatus(id: string, status: string, reason?: string) {
    const { data } = await api.patch(`/api/v1/deliveries/${id}/status`, { status, failure_reason: reason });
    return data;
  },

  async complete(id: string, payload: any) {
    const { data } = await api.post(`/api/v1/deliveries/${id}/complete`, payload);
    return data;
  },

  async delete(id: string) {
    const { data } = await api.delete(`/api/v1/deliveries/${id}`);
    return data;
  }
};
