'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { 
  Package, CheckCircle2, Clock, AlertTriangle, 
  TrendingUp, Users, Calendar, RefreshCw, Filter
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

export default function DashboardPage() {
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ['dashboard-stats', dateRange],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (dateRange.start) params.append('start_date', dateRange.start);
      if (dateRange.end) params.append('end_date', dateRange.end);
      const { data } = await api.get(`/api/v1/dashboard/stats?${params.toString()}`);
      return data;
    }
  });

  if (isLoading) return (
    <div className="flex items-center justify-center min-h-[400px]">
      <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );

  const kpis = [
    { label: 'Total Entregas', value: stats?.total || 0, icon: Package, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Completadas', value: stats?.delivered || 0, icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'En Progreso', value: stats?.in_progress || 0, icon: Clock, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { label: 'Pendientes', value: stats?.pending || 0, icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  ];

  const chartData = [
    { name: 'Pendiente', value: stats?.pending || 0, color: '#eab308' },
    { name: 'En Progreso', value: stats?.in_progress || 0, color: '#a855f7' },
    { name: 'Entregado', value: stats?.delivered || 0, color: '#10b981' },
    { name: 'Fallido', value: stats?.failed || 0, color: '#ef4444' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Header & Filters */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Panel de Control</h1>
          <p className="text-gray-500 mt-1">Monitoreo en tiempo real de operaciones logísticas.</p>
        </div>

        <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-2 rounded-2xl backdrop-blur-xl">
          <div className="flex items-center gap-2 px-3 border-r border-white/10">
            <Calendar className="w-4 h-4 text-gray-500" />
            <input 
              type="date" 
              value={dateRange.start}
              onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
              className="bg-transparent text-xs text-white outline-none"
            />
          </div>
          <div className="flex items-center gap-2 px-3">
            <input 
              type="date" 
              value={dateRange.end}
              onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
              className="bg-transparent text-xs text-white outline-none"
            />
          </div>
          <button 
            onClick={() => refetch()}
            className="p-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-white transition-all shadow-lg shadow-blue-600/20"
          >
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, i) => (
          <div key={i} className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-xl group hover:border-white/20 transition-all">
            <div className="flex justify-between items-start">
              <div className={`p-3 rounded-2xl ${kpi.bg} ${kpi.color}`}>
                <kpi.icon className="w-6 h-6" />
              </div>
              <TrendingUp className="w-4 h-4 text-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-500">{kpi.label}</p>
              <h3 className="text-3xl font-bold text-white mt-1">{kpi.value}</h3>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-xl">
          <h3 className="text-lg font-bold text-white mb-6">Rendimiento Operativo</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#6b7280', fontSize: 12}} />
                <Tooltip 
                  contentStyle={{backgroundColor: '#1e293b', border: '1px solid #ffffff10', borderRadius: '12px'}}
                  itemStyle={{color: '#fff'}}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distribution Chart */}
        <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-xl">
          <h3 className="text-lg font-bold text-white mb-6">Distribución de Estados</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{backgroundColor: '#1e293b', border: '1px solid #ffffff10', borderRadius: '12px'}}
                />
                <Legend iconType="circle" wrapperStyle={{fontSize: '12px', paddingTop: '20px'}} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Fleet Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-blue-600/10 to-indigo-600/10 border border-blue-500/20 p-6 rounded-3xl flex items-center gap-6">
          <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/20">
            <Users className="text-white w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-blue-400 font-bold uppercase tracking-wider">Flota de Repartidores</p>
            <h4 className="text-2xl font-bold text-white">{stats?.total_drivers || 0} registrados</h4>
            <p className="text-xs text-gray-500 mt-1">{stats?.active_drivers || 0} conductores activos hoy</p>
          </div>
        </div>

        <div className="bg-gradient-to-br from-emerald-600/10 to-teal-600/10 border border-emerald-500/20 p-6 rounded-3xl flex items-center gap-6">
          <div className="w-16 h-16 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-600/20">
            <CheckCircle2 className="text-white w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-emerald-400 font-bold uppercase tracking-wider">Tasa de Éxito</p>
            <h4 className="text-2xl font-bold text-white">{stats?.success_rate || 0}% efectividad</h4>
            <p className="text-xs text-gray-500 mt-1">Basado en entregas completadas vs totales</p>
          </div>
        </div>
      </div>
    </div>
  );
}
