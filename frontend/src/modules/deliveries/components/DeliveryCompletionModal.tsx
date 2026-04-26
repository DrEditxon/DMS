'use client';

import { useState, useEffect } from 'react';
import { CheckCircle2, MapPin, User, FileText, X, Loader2 } from 'lucide-react';
import SignaturePad from '@/components/SignaturePad';
import { deliveryService } from '../services/deliveryService';

interface Props {
  deliveryId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export default function DeliveryCompletionModal({ deliveryId, onSuccess, onCancel }: Props) {
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [receiverName, setReceiverName] = useState('');
  const [notes, setNotes] = useState('');
  const [signatureBase64, setSignatureBase64] = useState<string | null>(null);

  useEffect(() => {
    // Intentar obtener ubicación al abrir
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        (err) => setLocationError('No se pudo obtener la ubicación. Por favor activa el GPS.')
      );
    } else {
      setLocationError('Geolocalización no soportada en este navegador.');
    }
  }, []);

  const handleComplete = async () => {
    if (!signatureBase64 || !location || !receiverName) return;

    setLoading(true);
    try {
      await deliveryService.complete(deliveryId, {
        actual_receiver_name: receiverName,
        signature_base64: signatureBase64,
        lat: location.lat,
        lng: location.lng,
        notes: notes
      });
      onSuccess();
    } catch (error) {
      console.error('Error completing delivery:', error);
      alert('Error al completar la entrega.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface-900 border border-white/10 rounded-3xl p-8 max-w-xl w-full space-y-8 backdrop-blur-2xl shadow-2xl animate-in zoom-in-95 duration-300">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <CheckCircle2 className="w-6 h-6 text-emerald-400" />
          Finalizar Entrega
        </h2>
        <button onClick={onCancel} className="p-2 hover:bg-white/10 rounded-full text-gray-500 transition-all">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="space-y-6">
        {/* Receptor Name */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-400 flex items-center gap-2">
            <User className="w-4 h-4" /> Nombre de quien recibe *
          </label>
          <input
            type="text"
            value={receiverName}
            onChange={(e) => setReceiverName(e.target.value)}
            placeholder="Ej: Juan Pérez"
            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-blue-500/50 outline-none transition-all"
          />
        </div>

        {/* GPS Info */}
        <div className="p-4 bg-black/20 rounded-2xl border border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MapPin className={`w-5 h-5 ${location ? 'text-emerald-400' : 'text-yellow-400'}`} />
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase">Ubicación Actual</p>
              <p className="text-sm text-white">
                {location ? `${location.lat.toFixed(4)}, ${location.lng.toFixed(4)}` : (locationError || 'Obteniendo GPS...')}
              </p>
            </div>
          </div>
          {!location && !locationError && <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />}
        </div>

        {/* Signature Pad */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-400 flex items-center gap-2">
            Firma Digital *
          </label>
          <SignaturePad onSave={(base64) => setSignatureBase64(base64)} onClear={() => setSignatureBase64(null)} />
        </div>

        {/* Notes */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-400 flex items-center gap-2">
            <FileText className="w-4 h-4" /> Notas Adicionales
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            placeholder="Alguna observación sobre la entrega..."
            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-blue-500/50 outline-none transition-all resize-none"
          />
        </div>
      </div>

      <div className="flex gap-4 pt-4 border-t border-white/10">
        <button
          onClick={onCancel}
          className="flex-1 py-3 px-6 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all"
        >
          Cancelar
        </button>
        <button
          onClick={handleComplete}
          disabled={loading || !signatureBase64 || !location || !receiverName}
          className="flex-1 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-xl shadow-lg shadow-emerald-600/20 transition-all active:scale-95 flex items-center justify-center gap-2"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Confirmar Entrega'}
        </button>
      </div>
    </div>
  );
}
