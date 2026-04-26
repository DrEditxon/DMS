import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Delivery {
  id: string;
  tracking_no: string;
  status: string;
  recipient_name: string;
  scheduled_at: string;
  priority: number;
}

interface DeliveryState {
  deliveries: Delivery[];
  loading: boolean;
  error: string | null;
  setDeliveries: (deliveries: Delivery[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDeliveryStore = create<DeliveryState>()(
  persist(
    (set) => ({
      deliveries: [],
      loading: false,
      error: null,
      setDeliveries: (deliveries) => set({ deliveries }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
    }),
    {
      name: 'delivery-storage',
    }
  )
);
