"use client";

import dynamic from 'next/dynamic';

const MapView = dynamic(() => import('./MapView'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[400px] bg-slate-100 animate-pulse rounded-2xl flex items-center justify-center text-slate-400 font-medium">
      Cargando mapa...
    </div>
  )
});

export default MapView;
