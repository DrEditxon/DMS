"use client";

import React, { useState } from 'react';
import SignaturePad from '@/components/SignaturePad';
import { useParams, useRouter } from 'next/navigation';

export default function ProofPage() {
  const { id } = useParams();
  const router = useRouter();
  const [receiverName, setReceiverName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (signature: str, lat: number, lng: number) => {
    if (!receiverName) {
      alert("Por favor ingresa el nombre de quien recibe");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/deliveries/${id}/proof`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}` // Asumiendo que guardamos el token aquí
        },
        body: JSON.stringify({
          signature_base64: signature,
          latitude: lat,
          longitude: lng,
          receiver_name: receiverName
        })
      });

      if (response.ok) {
        alert("Entrega confirmada con éxito");
        router.push('/dashboard');
      } else {
        alert("Error al confirmar entrega");
      }
    } catch (error) {
      console.error(error);
      alert("Error de conexión");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900">Finalizar Entrega</h1>
          <p className="text-slate-500">ID de pedido: {id}</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-xl shadow-slate-200/50 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Nombre de quien recibe
            </label>
            <input 
              type="text" 
              value={receiverName}
              onChange={(e) => setReceiverName(e.target.value)}
              placeholder="Ej. Juan Pérez"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
          </div>

          <SignaturePad onSave={handleSubmit} />
        </div>

        {loading && (
          <div className="text-center text-blue-600 font-medium">
            Procesando entrega...
          </div>
        )}
      </div>
    </div>
  );
}
