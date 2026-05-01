"use client";

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Truck, Filter, Search, MoreVertical } from 'lucide-react';
import Link from 'next/link';

export default function DeliveriesPage() {
  const { data: deliveries, isLoading } = useQuery({
    queryKey: ['deliveries'],
    queryFn: async () => {
      const res = await api.get('/deliveries');
      return res.data;
    }
  });

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'delivered': return 'bg-emerald-100 text-emerald-700';
      case 'in_progress': return 'bg-blue-100 text-blue-700';
      case 'pending': return 'bg-slate-100 text-slate-700';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Entregas</h1>
          <p className="text-slate-500">Gestiona y monitorea todos tus envíos activos.</p>
        </div>
        <Link 
          href="/deliveries/new"
          className="px-6 py-2.5 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
        >
          + Nueva Entrega
        </Link>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex gap-4 items-center bg-slate-50/50">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Buscar por cliente o dirección..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border rounded-lg bg-white text-sm font-medium text-slate-600 hover:bg-slate-50 transition-all">
            <Filter className="w-4 h-4" />
            Filtros
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider font-semibold">
                <th className="px-6 py-4">Referencia</th>
                <th className="px-6 py-4">Cliente</th>
                <th className="px-6 py-4">Dirección</th>
                <th className="px-6 py-4">Estado</th>
                <th className="px-6 py-4">Fecha</th>
                <th className="px-6 py-4 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={6} className="px-6 py-4 bg-slate-50/20 h-16" />
                  </tr>
                ))
              ) : (
                deliveries?.map((d: any) => (
                  <tr key={d.id} className="hover:bg-slate-50 transition-colors group">
                    <td className="px-6 py-4">
                      <span className="font-mono text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        {d.tracking_number}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-900">{d.customer_name}</td>
                    <td className="px-6 py-4 text-sm text-slate-500 truncate max-w-[200px]">{d.address}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${getStatusStyle(d.status)}`}>
                        {d.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-500">
                      {new Date(d.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link 
                        href={`/deliveries/${d.id}`}
                        className="p-2 hover:bg-slate-100 rounded-lg inline-block text-slate-400 hover:text-slate-600"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
