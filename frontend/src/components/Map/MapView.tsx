"use client";

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix para los iconos de Leaflet en Next.js
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface MapViewProps {
  items: any[];
  center?: [number, number];
  zoom?: number;
}

function ChangeView({ center }: { center: [number, number] }) {
  const map = useMap();
  map.setView(center);
  return null;
}

export default function MapView({ items, center = [40.4168, -3.7038], zoom = 13 }: MapViewProps) {
  return (
    <div className="w-full h-full min-h-[400px] rounded-2xl overflow-hidden shadow-inner bg-slate-100 relative z-0">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        scrollWheelZoom={false}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ChangeView center={center} />
        {items.map((item) => (
          item.latitude && item.longitude && (
            <Marker 
              key={item.id} 
              position={[item.latitude, item.longitude]} 
              icon={icon}
            >
              <Popup className="custom-popup">
                <div className="p-1">
                  <p className="font-bold text-slate-900">{item.customer_name}</p>
                  <p className="text-xs text-slate-500">{item.address}</p>
                  <div className="mt-2 flex justify-between items-center gap-4">
                    <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold uppercase">
                      {item.status}
                    </span>
                    <a 
                      href={`/deliveries/${item.id}`}
                      className="text-[10px] text-blue-600 font-bold hover:underline"
                    >
                      Ver Detalle
                    </a>
                  </div>
                </div>
              </Popup>
            </Marker>
          )
        ))}
      </MapContainer>
    </div>
  );
}
