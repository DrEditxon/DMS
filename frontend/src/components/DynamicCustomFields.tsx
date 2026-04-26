'use client';

import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Calendar, Type, Hash, List as ListIcon, Loader2 } from 'lucide-react';

interface CustomFieldDef {
  id: string;
  name: string;
  label: string;
  field_type: 'TEXT' | 'NUMBER' | 'DATE' | 'SELECT' | 'BOOLEAN';
  is_required: bool;
  options?: string[];
  placeholder?: string;
  help_text?: string;
}

interface Props {
  entityId?: string;
  appliesTo?: 'delivery' | 'item';
  onChange?: (values: Record<string, any>) => void;
  initialValues?: Record<string, any>;
}

export default function DynamicCustomFields({ entityId, appliesTo = 'delivery', onChange, initialValues = {} }: Props) {
  const [fields, setFields] = useState<CustomFieldDef[]>([]);
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        // 1. Cargar definiciones
        const { data: defs } = await api.get(`/api/v1/custom-fields/?applies_to=${appliesTo}`);
        setFields(defs);

        // 2. Cargar valores si hay entityId
        if (entityId) {
          const { data: savedValues } = await api.get(`/api/v1/custom-fields/values/${entityId}`);
          setValues(prev => ({ ...prev, ...savedValues }));
        }
      } catch (err) {
        console.error('Error loading custom fields:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [entityId, appliesTo]);

  const handleChange = (name: string, val: any) => {
    const newValues = { ...values, [name]: val };
    setValues(newValues);
    if (onChange) onChange(newValues);
  };

  if (loading) return <div className="flex items-center gap-2 text-gray-500 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Cargando campos extra...</div>;
  if (fields.length === 0) return null;

  return (
    <div className="space-y-4 p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-xl">
      <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Campos Personalizados</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map((field) => (
          <div key={field.id} className="space-y-1.5">
            <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
              {field.field_type === 'TEXT' && <Type className="w-3.5 h-3.5 text-blue-400" />}
              {field.field_type === 'NUMBER' && <Hash className="w-3.5 h-3.5 text-emerald-400" />}
              {field.field_type === 'DATE' && <Calendar className="w-3.5 h-3.5 text-purple-400" />}
              {field.field_type === 'SELECT' && <ListIcon className="w-3.5 h-3.5 text-orange-400" />}
              {field.label}
              {field.is_required && <span className="text-red-500">*</span>}
            </label>

            {field.field_type === 'SELECT' ? (
              <select
                value={values[field.name] || ''}
                onChange={(e) => handleChange(field.name, e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:border-blue-500/50 outline-none transition-all"
              >
                <option value="">Seleccionar...</option>
                {field.options?.map(opt => <option key={opt} value={opt}>{opt}</option>)}
              </select>
            ) : field.field_type === 'DATE' ? (
              <input
                type="date"
                value={values[field.name] || ''}
                onChange={(e) => handleChange(field.name, e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:border-blue-500/50 outline-none"
              />
            ) : (
              <input
                type={field.field_type === 'NUMBER' ? 'number' : 'text'}
                value={values[field.name] || ''}
                placeholder={field.placeholder || `Ingrese ${field.label.toLowerCase()}`}
                onChange={(e) => handleChange(field.name, field.field_type === 'NUMBER' ? parseFloat(e.target.value) : e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:border-blue-500/50 outline-none placeholder:text-gray-600"
              />
            )}
            {field.help_text && <p className="text-[10px] text-gray-500 px-1">{field.help_text}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
