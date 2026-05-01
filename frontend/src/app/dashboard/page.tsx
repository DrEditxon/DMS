"use client";

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { 
  Package, 
  Clock, 
  CheckCircle2, 
  TrendingUp,
  Calendar
} from 'lucide-react';
import StatsChart from '@/components/StatsChart';

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await api.get('/stats');
      return res.data;
    }
  });

  const cards = [
    { label: 'Entregas Totales', value: stats?.total || 0, icon: Package, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'En Tránsito', value: stats?.in_progress || 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: 'Completadas', value: stats?.completed || 0, icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: 'Pendientes', value: stats?.pending || 0, icon: TrendingUp, color: 'text-purple-600', bg: 'bg-purple-50' },
  ];

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dashboard Operativo</h1>
          <p className="text-slate-500">Resumen de actividad logística en tiempo real.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-white border rounded-xl text-sm font-medium text-slate-600 shadow-sm cursor-pointer hover:bg-slate-50">
          <Calendar className="w-4 h-4" />
          Últimos 7 días
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex items-center gap-4 transition-all hover:shadow-md hover:-translate-y-1">
              <div className={`w-14 h-14 ${stat.bg} rounded-2xl flex items-center justify-center`}>
                <Icon className={`w-7 h-7 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-400">{stat.label}</p>
                <p className="text-3xl font-bold text-slate-900">
                  {isLoading ? '...' : stat.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-xl font-bold text-slate-900">Tendencia de Entregas</h2>
            <span className="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full uppercase tracking-wider">
              Volumen Diario
            </span>
          </div>
          {isLoading ? (
            <div className="h-[300px] bg-slate-50 animate-pulse rounded-2xl" />
          ) : (
            <StatsChart data={stats?.history || []} />
          )}
        </div>

        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 flex flex-col justify-center text-center gap-4">
          <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto flex items-center justify-center shadow-xl shadow-blue-200">
            <CheckCircle2 className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-slate-900">Buen Trabajo</h3>
          <p className="text-slate-500 text-sm">Has completado el 85% de las entregas programadas para hoy.</p>
          <button className="mt-4 px-6 py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all">
            Ver Reporte Detallado
          </button>
        </div>
      </div>
    </div>
  );
}
