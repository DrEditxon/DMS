"use client";

import MapView from '@/components/Map';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import Sidebar from '@/components/Sidebar';

export default function GlobalMapPage() {
  const { data: deliveries } = useQuery({
    queryKey: ['deliveries'],
    queryFn: async () => {
      const res = await api.get('/deliveries');
      return res.data;
    }
  });

  return (
    <div className="flex bg-slate-50 min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-64 p-8 flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Mapa de Operaciones</h1>
          <p className="text-slate-500">Visualiza la ubicación de todas tus entregas en tiempo real.</p>
        </div>

        <div className="flex-1 min-h-[600px] bg-white p-2 rounded-3xl shadow-xl shadow-slate-200 border border-slate-100">
          <MapView items={deliveries || []} />
        </div>
      </main>
    </div>
  );
}
