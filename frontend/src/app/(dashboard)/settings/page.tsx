'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Settings2, Plus, Trash2, Save, Type, Hash, Calendar, List as ListIcon } from 'lucide-react';

export default function SettingsPage() {
  const [fields, setFields] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // New field state
  const [newField, setNewField] = useState({
    name: '',
    label: '',
    field_type: 'TEXT',
    applies_to: 'delivery',
    is_required: false,
    options: '',
  });

  useEffect(() => {
    fetchFields();
  }, []);

  const fetchFields = async () => {
    try {
      const { data } = await api.get('/api/v1/custom-fields/');
      setFields(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddField = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const payload = {
        ...newField,
        options: newField.field_type === 'SELECT' ? newField.options.split(',').map(o => o.trim()) : null
      };
      await api.post('/api/v1/custom-fields/', payload);
      setNewField({ name: '', label: '', field_type: 'TEXT', applies_to: 'delivery', is_required: false, options: '' });
      fetchFields();
    } catch (err) {
      alert('Error al crear campo. Verifica que el nombre sea único y snake_case.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10">
      <div className="page-header">
        <h1 className="page-title flex items-center gap-2">
          <Settings2 className="w-8 h-8 text-blue-500" />
          Configuración del Sistema
        </h1>
        <p className="page-subtitle">Personaliza los datos y el comportamiento de tu plataforma.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario de creación */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
            <h3 className="text-lg font-bold text-white mb-4">Nuevo Campo</h3>
            <form onSubmit={handleAddField} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs text-gray-400">ID Interno (snake_case) *</label>
                <input 
                  value={newField.name}
                  onChange={e => setNewField({...newField, name: e.target.value})}
                  placeholder="ej: color_paquete"
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white outline-none focus:border-blue-500/50"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs text-gray-400">Etiqueta UI *</label>
                <input 
                  value={newField.label}
                  onChange={e => setNewField({...newField, label: e.target.value})}
                  placeholder="ej: Color del Paquete"
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white outline-none focus:border-blue-500/50"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs text-gray-400">Tipo de Dato</label>
                <select 
                  value={newField.field_type}
                  onChange={e => setNewField({...newField, field_type: e.target.value})}
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white outline-none"
                >
                  <option value="TEXT">Texto Corto</option>
                  <option value="NUMBER">Número</option>
                  <option value="DATE">Fecha</option>
                  <option value="SELECT">Selección (Dropdown)</option>
                </select>
              </div>

              {newField.field_type === 'SELECT' && (
                <div className="space-y-1 animate-in fade-in slide-in-from-top-2">
                  <label className="text-xs text-gray-400">Opciones (separadas por coma)</label>
                  <input 
                    value={newField.options}
                    onChange={e => setNewField({...newField, options: e.target.value})}
                    placeholder="Rojo, Verde, Azul"
                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white outline-none"
                    required
                  />
                </div>
              )}

              <div className="flex items-center gap-2 py-2">
                <input 
                  type="checkbox"
                  checked={newField.is_required}
                  onChange={e => setNewField({...newField, is_required: e.target.checked})}
                  className="w-4 h-4 accent-blue-600"
                />
                <label className="text-sm text-gray-300">Es obligatorio</label>
              </div>

              <button 
                type="submit"
                disabled={isSaving}
                className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2"
              >
                {isSaving ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Plus className="w-5 h-5" /> Crear Campo</>}
              </button>
            </form>
          </div>
        </div>

        {/* Listado de campos */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-bold text-white">Campos Activos</h3>
            <span className="text-xs text-gray-500">{fields.length} campos configurados</span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {loading ? (
              <div className="p-12 text-center text-gray-500">Cargando configuración...</div>
            ) : fields.length === 0 ? (
              <div className="p-12 text-center bg-white/5 border border-dashed border-white/10 rounded-2xl text-gray-500 italic">
                No hay campos personalizados configurados.
              </div>
            ) : fields.map((field) => (
              <div key={field.id} className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center justify-between group hover:bg-white/10 transition-all">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-black/20 flex items-center justify-center text-blue-400">
                    {field.field_type === 'TEXT' && <Type className="w-6 h-6" />}
                    {field.field_type === 'NUMBER' && <Hash className="w-6 h-6 text-emerald-400" />}
                    {field.field_type === 'DATE' && <Calendar className="w-6 h-6 text-purple-400" />}
                    {field.field_type === 'SELECT' && <ListIcon className="w-6 h-6 text-orange-400" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-bold text-white">{field.label}</p>
                      {field.is_required && <span className="text-[10px] bg-red-500/20 text-red-400 px-1.5 rounded uppercase">Obligatorio</span>}
                    </div>
                    <p className="text-xs text-gray-500 font-mono">slug: {field.name}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="hidden md:block text-right">
                    <p className="text-xs text-gray-400">Tipo: {field.field_type}</p>
                    <p className="text-[10px] text-gray-600">ID: {field.id.slice(0, 8)}</p>
                  </div>
                  <button className="p-2 text-gray-600 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all opacity-0 group-hover:opacity-100">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
