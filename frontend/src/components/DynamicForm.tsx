"use client";

import React, { useEffect, useState } from 'react';

interface CustomField {
  id: str;
  name: str;
  label: str;
  data_type: 'text' | 'number' | 'date' | 'select';
  options?: str[];
}

export default function DynamicForm({ deliveryId }: { deliveryId: str }) {
  const [fields, setFields] = useState<CustomField[]>([]);
  const [values, setValues] = useState<Record<str, any>>({});

  useEffect(() => {
    // 1. Cargar definiciones de campos
    fetch('http://localhost:8000/api/v1/custom-fields', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    .then(res => res.json())
    .then(data => setFields(data));

    // 2. Cargar valores actuales de la entrega
    fetch(`http://localhost:8000/api/v1/custom-fields/${deliveryId}/values`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    .then(res => res.json())
    .then(data => {
      const valMap: any = {};
      data.forEach((v: any) => valMap[v.field_id] = v.value);
      setValues(valMap);
    });
  }, [deliveryId]);

  const handleChange = (fieldId: str, value: any) => {
    setValues(prev => ({ ...prev, [fieldId]: value }));
  };

  const save = async () => {
    const payload = Object.entries(values).map(([fieldId, value]) => ({
      field_id: fieldId,
      value: value.toString()
    }));

    await fetch(`http://localhost:8000/api/v1/custom-fields/${deliveryId}/values`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` 
      },
      body: JSON.stringify(payload)
    });
    alert("Campos personalizados guardados");
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col gap-6">
      <h3 className="text-lg font-bold text-slate-800">Información Adicional</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map(field => (
          <div key={field.id} className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-600">{field.label}</label>
            {field.data_type === 'select' ? (
              <select 
                value={values[field.id] || ""}
                onChange={(e) => handleChange(field.id, e.target.value)}
                className="px-3 py-2 border rounded-lg bg-slate-50 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              >
                <option value="">Seleccionar...</option>
                {field.options?.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : (
              <input 
                type={field.data_type === 'number' ? 'number' : field.data_type === 'date' ? 'date' : 'text'}
                value={values[field.id] || ""}
                onChange={(e) => handleChange(field.id, e.target.value)}
                className="px-3 py-2 border rounded-lg bg-slate-50 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
            )}
          </div>
        ))}
      </div>
      <button 
        onClick={save}
        className="w-full md:w-auto self-end px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-all font-medium"
      >
        Guardar Datos Extra
      </button>
    </div>
  );
}
