'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { 
  Package, MapPin, User, Phone, Mail, Clock, 
  ChevronLeft, MoreVertical, Edit2, Map as MapIcon,
  CheckCircle, AlertCircle, RefreshCw, ClipboardList
} from 'lucide-react';
import { deliveryService } from '@/modules/deliveries/services/deliveryService';
import dynamic from 'next/dynamic';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

// Importación dinámica del mapa para evitar errores de SSR
const DeliveryMap = dynamic(() => import('@/modules/deliveries/components/DeliveryMap'), { 
  ssr: false,
  loading: () => <div className="h-[400px] bg-white/5 rounded-2xl animate-pulse" />
});

export default function DeliveryDetailPage() {
  const { id } = useParams();
  const router = useRouter();

  const { data: delivery, isLoading, error, refetch } = useQuery({
    queryKey: ['delivery', id],
    queryFn: () => deliveryService.getById(id as string),
  });

  if (isLoading) return <div className="flex items-center justify-center min-h-[400px]"><RefreshCw className="w-8 h-8 text-blue-500 animate-spin" /></div>;
  if (error || !delivery) return <div className="p-8 text-center text-red-400">Error al cargar los detalles de la entrega.</div>;

  const statusColors: Record<string, string> = {
    PENDING: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    ASSIGNED: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    IN_PROGRESS: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
    DELIVERED: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    FAILED: 'bg-red-500/10 text-red-500 border-red-500/20',
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => router.back()}
            className="p-2 hover:bg-white/5 rounded-xl text-gray-500 hover:text-white transition-all"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <div>
            <nav className="text-xs text-gray-500 uppercase tracking-widest mb-1">Entregas / Detalle</nav>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              {delivery.tracking_no}
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${statusColors[delivery.status]}`}>
                {delivery.status}
              </span>
            </h1>
          </div>
        </div>

        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-gray-300 hover:bg-white/10 transition-all font-medium">
            <Edit2 className="w-4 h-4" /> Editar
          </button>
          <button className="p-2.5 bg-white/5 border border-white/10 rounded-xl text-gray-300 hover:bg-white/10 transition-all">
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Details & Map */}
        <div className="lg:col-span-2 space-y-8">
          {/* Map Card */}
          <div className="bg-white/5 border border-white/10 rounded-3xl overflow-hidden shadow-2xl relative">
            <div className="absolute top-4 left-4 z-10 bg-surface-900/80 backdrop-blur-md p-3 rounded-2xl border border-white/10 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
                <MapPin className="text-white w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">Dirección de Entrega</p>
                <p className="text-sm text-white font-medium">{delivery.address?.street}, {delivery.address?.city}</p>
              </div>
            </div>
            <DeliveryMap 
              deliveries={[{
                ...delivery,
                lat: delivery.address?.lat || 4.6097,
                lng: delivery.address?.lng || -74.0817
              }]} 
            />
          </div>

          {/* Items Table */}
          <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl">
            <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-blue-400" />
              Productos en el Pedido
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/5 text-gray-500 text-xs uppercase tracking-widest">
                    <th className="py-3 px-2">Producto</th>
                    <th className="py-3 px-2">SKU</th>
                    <th className="py-3 px-2">Cant.</th>
                    <th className="py-3 px-2">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {delivery.items?.map((item: any) => (
                    <tr key={item.id} className="text-sm">
                      <td className="py-4 px-2 font-medium text-white">{item.name}</td>
                      <td className="py-4 px-2 text-gray-400 font-mono">{item.sku || 'N/A'}</td>
                      <td className="py-4 px-2 text-gray-300">{item.quantity} {item.unit}</td>
                      <td className="py-4 px-2">
                        <span className="inline-flex w-2 h-2 rounded-full bg-blue-500 mr-2 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
                        <span className="text-gray-400 text-xs">Preparado</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: Sidebar info */}
        <div className="space-y-6">
          {/* Recipient Card */}
          <div className="bg-white/5 border border-white/10 rounded-3xl p-6 space-y-6">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest">Cliente y Destino</h3>
            
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xl font-bold text-white border border-white/10">
                {delivery.recipient_name.charAt(0)}
              </div>
              <div>
                <p className="text-lg font-bold text-white">{delivery.recipient_name}</p>
                <p className="text-xs text-gray-500">Destinatario Final</p>
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-white/5">
              <div className="flex items-center gap-3 text-gray-300">
                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-gray-500"><Phone className="w-4 h-4" /></div>
                <span className="text-sm">{delivery.recipient_phone || 'Sin teléfono'}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-300">
                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-gray-500"><Mail className="w-4 h-4" /></div>
                <span className="text-sm truncate">{delivery.recipient_email || 'Sin correo'}</span>
              </div>
            </div>
          </div>

          {/* Logistics Card */}
          <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-500/20 rounded-3xl p-6 space-y-6">
            <h3 className="text-sm font-bold text-blue-400/60 uppercase tracking-widest">Estado Logístico</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-gray-300">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-xs">Programado:</span>
                </div>
                <span className="text-xs font-bold text-white">{format(new Date(delivery.scheduled_at), "d 'de' MMMM, HH:mm", { locale: es })}</span>
              </div>

              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-gray-300">
                  <User className="w-4 h-4 text-gray-500" />
                  <span className="text-xs">Repartidor:</span>
                </div>
                <span className="text-xs font-bold text-white">{delivery.driver?.full_name || 'Sin asignar'}</span>
              </div>

              <div className="pt-4 mt-4 border-t border-white/10">
                <p className="text-xs text-gray-500 mb-2">Historial reciente</p>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
                    <div>
                      <p className="text-xs text-white font-medium">Entrega Creada</p>
                      <p className="text-[10px] text-gray-500">{format(new Date(delivery.created_at), 'HH:mm')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
