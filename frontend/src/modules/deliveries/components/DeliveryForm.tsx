'use client';

import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Package, Plus, Trash2, MapPin, Calendar, Save, X, Settings2 } from 'lucide-react';
import { deliveryService } from '../services/deliveryService';
import DynamicCustomFields from '@/components/DynamicCustomFields';
import api from '@/lib/api';

const itemSchema = z.object({
  name: z.string().min(2, 'Nombre requerido'),
  sku: z.string().optional(),
  quantity: z.number().gt(0),
  unit: z.string().default('unidad'),
});

const deliverySchema = z.object({
  tracking_no: z.string().min(3).regex(/^[A-Za-z0-9\-_]+$/),
  recipient_name: z.string().min(2),
  recipient_phone: z.string().optional(),
  recipient_email: z.string().email().optional().or(z.literal('')),
  scheduled_at: z.string(),
  priority: z.number().min(1).max(5).default(3),
  address: z.object({
    street: z.string().min(3),
    city: z.string().min(2),
    country: z.string().default('Colombia'),
  }),
  items: z.array(itemSchema).min(1, 'Al menos un ítem es requerido'),
});

type DeliveryFormValues = z.infer<typeof deliverySchema>;

export default function DeliveryForm({ onSuccess, onCancel }: { onSuccess?: () => void, onCancel?: () => void }) {
  const [loading, setLoading] = useState(false);
  const [customValues, setCustomValues] = useState<Record<string, any>>({});

  const { register, control, handleSubmit, formState: { errors } } = useForm<DeliveryFormValues>({
    resolver: zodResolver(deliverySchema),
    defaultValues: {
      priority: 3,
      items: [{ name: '', quantity: 1, unit: 'unidad' }],
      address: { country: 'Colombia' }
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "items"
  });

  const onSubmit = async (data: DeliveryFormValues) => {
    setLoading(true);
    try {
      // Ajustar formato de fecha para el backend (ISO string)
      const payload = {
        ...data,
        scheduled_at: new Date(data.scheduled_at).toISOString(),
        recipient_email: data.recipient_email || null
      };
      
      // 1. Crear entrega principal
      const created = await deliveryService.create(payload);

      // 2. Guardar valores personalizados si existen
      if (Object.keys(customValues).length > 0) {
        await api.post(`/api/v1/custom-fields/values/${created.id}`, { values: customValues });
      }

      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Error creating delivery:', error);
      alert('Error al crear la entrega. Verifica los datos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8 bg-white/5 p-8 rounded-3xl border border-white/10 backdrop-blur-2xl">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Package className="w-6 h-6 text-blue-400" />
          Nueva Entrega
        </h2>
        <button type="button" onClick={onCancel} className="p-2 hover:bg-white/10 rounded-full text-gray-500 transition-all">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Información General */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
            Información del Cliente
          </h3>
          <div className="space-y-3">
            <input
              {...register('tracking_no')}
              placeholder="Número de Tracking (Ej: TRK-001)"
              className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:border-blue-500/50 outline-none transition-all"
            />
            {errors.tracking_no && <p className="text-red-400 text-xs">{errors.tracking_no.message}</p>}

            <input
              {...register('recipient_name')}
              placeholder="Nombre del Destinatario"
              className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:border-blue-500/50 outline-none transition-all"
            />
            
            <div className="grid grid-cols-2 gap-3">
              <input
                {...register('recipient_phone')}
                placeholder="Teléfono"
                className="bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 outline-none"
              />
              <input
                {...register('recipient_email')}
                placeholder="Email (Opcional)"
                className="bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Logística */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
            Detalles Logísticos
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 bg-black/20 border border-white/10 rounded-xl px-4 py-3">
              <Calendar className="w-5 h-5 text-gray-500" />
              <input
                {...register('scheduled_at')}
                type="datetime-local"
                className="bg-transparent text-white outline-none w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-500 px-1">Prioridad (1: Alta, 5: Baja)</label>
              <input
                {...register('priority', { valueAsNumber: true })}
                type="range" min="1" max="5"
                className="w-full accent-blue-500"
              />
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 bg-black/20 border border-white/10 rounded-xl px-4 py-3">
                <MapPin className="w-5 h-5 text-gray-500" />
                <input {...register('address.street')} placeholder="Calle y Número" className="bg-transparent text-white outline-none flex-1" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input {...register('address.city')} placeholder="Ciudad" className="bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white outline-none" />
                <input {...register('address.country')} placeholder="País" className="bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white outline-none" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic Custom Fields */}
      <DynamicCustomFields 
        appliesTo="delivery" 
        onChange={(vals) => setCustomValues(vals)} 
      />

      {/* Items Section */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Ítems del Pedido</h3>
          <button 
            type="button" 
            onClick={() => append({ name: '', quantity: 1, unit: 'unidad' })}
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
          >
            <Plus className="w-4 h-4" /> Agregar Ítem
          </button>
        </div>

        <div className="space-y-3">
          {fields.map((field, index) => (
            <div key={field.id} className="grid grid-cols-12 gap-3 items-center animate-in fade-in slide-in-from-top-2">
              <div className="col-span-6">
                <input
                  {...register(`items.${index}.name` as const)}
                  placeholder="Nombre del producto"
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500/30"
                />
              </div>
              <div className="col-span-2">
                <input
                  {...register(`items.${index}.quantity` as const, { valueAsNumber: true })}
                  type="number"
                  placeholder="Cant"
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white outline-none"
                />
              </div>
              <div className="col-span-3">
                <select 
                  {...register(`items.${index}.unit` as const)}
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white outline-none"
                >
                  <option value="unidad">Unidades</option>
                  <option value="kg">Kilos</option>
                  <option value="caja">Cajas</option>
                </select>
              </div>
              <div className="col-span-1 text-right">
                <button type="button" onClick={() => remove(index)} className="p-2 text-red-500/50 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
          {errors.items && <p className="text-red-400 text-xs">{errors.items.message}</p>}
        </div>
      </div>

      <div className="flex justify-end gap-4 pt-4 border-t border-white/10">
        <button 
          type="button" 
          onClick={onCancel}
          className="px-6 py-3 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all active:scale-95"
        >
          {loading ? 'Guardando...' : <><Save className="w-5 h-5" /> Guardar Entrega</>}
        </button>
      </div>
    </form>
  );
}
