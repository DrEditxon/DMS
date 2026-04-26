'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import dynamic from 'next/dynamic';
import api from '@/lib/api';
import { deliveryService } from '@/modules/deliveries/services/deliveryService';
import DeliveryList from '@/modules/deliveries/components/DeliveryList';
import DeliveryForm from '@/modules/deliveries/components/DeliveryForm';
import { Plus, Download, RefreshCw, Map as MapIcon, List as ListIcon, FileText, Loader2 } from 'lucide-react';

const DeliveryMap = dynamic(() => import('@/modules/deliveries/components/DeliveryMap'), { 
  ssr: false,
  loading: () => <div className="h-[600px] bg-white/5 rounded-3xl animate-pulse" />
});

export default function DeliveriesPage() {
  const [showForm, setShowForm] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [exporting, setExporting] = useState<string | null>(null);

  const handleExport = async (format: 'excel' | 'pdf') => {
    setExporting(format);
    try {
      // Nota: En un sistema real, pasaríamos los filtros actuales aquí
      const response = await api.get(`/api/v1/deliveries/export/${format}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const ext = format === 'excel' ? 'xlsx' : 'pdf';
      link.setAttribute('download', `reporte_entregas_${new Date().getTime()}.${ext}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export error:', err);
      alert('Error al generar el reporte.');
    } finally {
      setExporting(null);
    }
  };

  const { data } = useQuery({
    queryKey: ['deliveries', { status: '', search: '' }],
    queryFn: () => deliveryService.getAll({ status: '', search: '' }),
  });

  const handleSuccess = () => {
    setShowForm(false);
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-8 min-h-screen">
      {/* Action Bar */}
      <div className="flex justify-between items-center">
        <div className="hidden md:block">
          <nav className="text-sm text-gray-500 mb-1">
            Dashboard / <span className="text-blue-400">Entregas</span>
          </nav>
        </div>
        
        <div className="flex gap-3 w-full md:w-auto">
          {/* View Toggle */}
          <div className="flex bg-white/5 border border-white/10 rounded-xl p-1">
            <button 
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-all ${viewMode === 'list' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
            >
              <ListIcon className="w-5 h-5" />
            </button>
            <button 
              onClick={() => setViewMode('map')}
              className={`p-2 rounded-lg transition-all ${viewMode === 'map' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
            >
              <MapIcon className="w-5 h-5" />
            </button>
          </div>

          <button 
            onClick={() => setRefreshKey(prev => prev + 1)}
            className="p-3 bg-white/5 border border-white/10 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-all"
            title="Refrescar lista"
          >
            <RefreshCw className="w-5 h-5" />
          </button>

          <div className="flex gap-2">
            <button 
              onClick={() => handleExport('excel')}
              disabled={exporting === 'excel'}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-600/20 rounded-xl transition-all text-sm font-bold"
            >
              {exporting === 'excel' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Excel
            </button>
            <button 
              onClick={() => handleExport('pdf')}
              disabled={exporting === 'pdf'}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/10 border border-red-500/20 text-red-400 hover:bg-red-600/20 rounded-xl transition-all text-sm font-bold"
            >
              {exporting === 'pdf' ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              PDF
            </button>
          </div>
          
          <button 
            onClick={() => setShowForm(true)}
            className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-600/20 transition-all active:scale-95"
          >
            <Plus className="w-5 h-5" />
            Nueva Entrega
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative animate-in fade-in duration-500">
        {viewMode === 'list' ? (
          <DeliveryList key={refreshKey} />
        ) : (
          <div className="h-[600px] w-full">
            <DeliveryMap 
              deliveries={(data?.items || []).map((d: any) => ({
                ...d,
                lat: d.address?.lat || 4.6097,
                lng: d.address?.lng || -74.0817
              }))} 
            />
          </div>
        )}
      </div>

      {/* Overlay Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto no-scrollbar rounded-3xl shadow-2xl animate-in zoom-in-95 duration-300">
            <DeliveryForm 
              onSuccess={handleSuccess} 
              onCancel={() => setShowForm(false)} 
            />
          </div>
        </div>
      )}
    </div>
  );
}
