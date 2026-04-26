import { useQuery } from '@tanstack/react-query';
import { Package, Clock, User, ChevronRight, Filter, CheckCircle2, RefreshCw } from 'lucide-react';
import DeliveryCompletionModal from './DeliveryCompletionModal';

export default function DeliveryList() {
  const [filters, setFilters] = useState({ status: '', search: '' });
  const [selectedForCompletion, setSelectedForCompletion] = useState<string | null>(null);

  const { data, isLoading, isRefetching, refetch } = useQuery({
    queryKey: ['deliveries', filters],
    queryFn: () => deliveryService.getAll(filters),
  });

  const deliveries = data?.items || [];

  const statusColors: Record<string, string> = {
    PENDING: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    ASSIGNED: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    IN_PROGRESS: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
    DELIVERED: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    FAILED: 'bg-red-500/10 text-red-500 border-red-500/20',
    CANCELLED: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
  };

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">Entregas</h2>
          <p className="text-gray-400 text-sm">Gestiona y monitorea todas las órdenes en tiempo real.</p>
        </div>
        
        <div className="flex gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Buscar tracking, cliente..."
              className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <select 
            className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="">Todos los estados</option>
            <option value="PENDING">Pendiente</option>
            <option value="IN_PROGRESS">En camino</option>
            <option value="DELIVERED">Entregado</option>
          </select>
        </div>
      </div>

      {/* Table / List */}
      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden backdrop-blur-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/10 bg-white/5">
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Tracking / Cliente</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Prioridad</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Programada</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Repartidor</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    <div className="flex flex-col items-center gap-3">
                      <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
                      Cargando entregas...
                    </div>
                  </td>
                </tr>
              ) : deliveries.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">No se encontraron entregas.</td>
                </tr>
              ) : (
                deliveries.map((delivery) => (
                  <tr key={delivery.id} className="hover:bg-white/5 transition-colors group cursor-pointer">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
                          <Package className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="font-medium text-white group-hover:text-blue-400 transition-colors">{delivery.tracking_no}</p>
                          <p className="text-sm text-gray-400">{delivery.recipient_name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[delivery.status]}`}>
                        {delivery.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((lvl) => (
                          <div 
                            key={lvl} 
                            className={`w-1.5 h-3 rounded-full ${lvl <= (6 - delivery.priority) ? 'bg-blue-500' : 'bg-white/10'}`}
                          />
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-gray-300">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <span className="text-sm">{new Date(delivery.scheduled_at).toLocaleDateString()}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-300">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center">
                          <User className="w-3 h-3 text-gray-400" />
                        </div>
                        <span className="text-sm">Sin asignar</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        {delivery.status === 'IN_PROGRESS' && (
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedForCompletion(delivery.id);
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 rounded-lg text-xs font-bold transition-all"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" /> Finalizar
                          </button>
                        )}
                        <button className="p-2 hover:bg-white/10 rounded-lg text-gray-500 hover:text-white transition-all">
                          <ChevronRight className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Completion Modal */}
      {selectedForCompletion && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <DeliveryCompletionModal
            deliveryId={selectedForCompletion}
            onSuccess={() => {
              setSelectedForCompletion(null);
              refetch();
            }}
            onCancel={() => setSelectedForCompletion(null)}
          />
        </div>
      )}
    </div>
  );
}
