"use client";

import React, { useRef, useState, useEffect } from 'react';

interface SignaturePadProps {
  onSave: (signatureBase64: str, latitude: number, longitude: number) => void;
}

export default function SignaturePad({ onSave }: SignaturePadProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    // Obtener ubicación automáticamente al cargar
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
      });
    }
  }, []);

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true);
    draw(e);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx?.beginPath();
    }
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000';

    const rect = canvas.getBoundingClientRect();
    const x = ('touches' in e) ? e.touches[0].clientX - rect.left : (e as React.MouseEvent).clientX - rect.left;
    const y = ('touches' in e) ? e.touches[0].clientY - rect.top : (e as React.MouseEvent).clientY - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const handleSave = () => {
    if (!canvasRef.current || !location) {
      alert("Falta firma o ubicación");
      return;
    }
    const signatureBase64 = canvasRef.current.toDataURL("image/png");
    onSave(signatureBase64, location.lat, location.lng);
  };

  const clear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (canvas && ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4 border rounded-xl bg-white shadow-sm">
      <h3 className="text-lg font-semibold text-slate-800">Firma de Recepción</h3>
      <canvas
        ref={canvasRef}
        onMouseDown={startDrawing}
        onMouseUp={stopDrawing}
        onMouseMove={draw}
        onTouchStart={startDrawing}
        onTouchEnd={stopDrawing}
        onTouchMove={draw}
        width={400}
        height={200}
        className="border-2 border-dashed border-slate-300 rounded-lg cursor-crosshair touch-none"
      />
      <div className="flex justify-between items-center">
        <button 
          onClick={clear}
          className="text-sm text-slate-500 hover:text-red-500 transition-colors"
        >
          Limpiar
        </button>
        <button 
          onClick={handleSave}
          disabled={!location}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-slate-300 transition-all shadow-md active:scale-95"
        >
          {location ? "Confirmar Entrega" : "Obteniendo ubicación..."}
        </button>
      </div>
      {location && (
        <p className="text-[10px] text-slate-400">
          Ubicación capturada: {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
        </p>
      )}
    </div>
  );
}
