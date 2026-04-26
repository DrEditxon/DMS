'use client';

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect } from 'react';
import { Truck, Package, CheckCircle, AlertCircle } from 'lucide-react';
import { renderToStaticMarkup } from 'react-dom/server';

// Fix for Leaflet marker icons
const fixIcons = () => {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  });
};

// Component to handle auto-fitting bounds when deliveries change
function ChangeView({ bounds }: { bounds: L.LatLngBoundsExpression | null }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) map.fitBounds(bounds, { padding: [50, 50] });
  }, [bounds, map]);
  return null;
}

// Function to create a custom div icon based on status
const createCustomIcon = (status: string, isMain: boolean = false) => {
  const color = 
    status === 'DELIVERED' ? '#10b981' : 
    status === 'IN_PROGRESS' ? '#8b5cf6' : 
    status === 'FAILED' ? '#ef4444' : 
    '#3b82f6';

  const iconMarkup = renderToStaticMarkup(
    <div style={{ 
      color, 
      backgroundColor: 'rgba(15, 23, 42, 0.8)',
      padding: '8px',
      borderRadius: '12px',
      border: `2px solid ${color}`,
      boxShadow: `0 0 15px ${color}44`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {isMain ? <Truck size={20} /> : <Package size={16} />}
    </div>
  );

  return L.divIcon({
    html: iconMarkup,
    className: 'custom-leaflet-icon',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });
};

interface DeliveryPoint {
  id: string;
  tracking_no: string;
  status: string;
  recipient_name: string;
  lat: number;
  lng: number;
}

interface Props {
  deliveries: DeliveryPoint[];
  center?: [number, number];
  zoom?: number;
  className?: string;
}

export default function DeliveryMap({ deliveries, center, zoom = 13, className }: Props) {
  useEffect(() => { fixIcons(); }, []);

  const defaultCenter: [number, number] = center || (deliveries.length > 0 ? [deliveries[0].lat, deliveries[0].lng] : [4.6097, -74.0817]);

  // Calculate bounds if there are multiple deliveries
  const bounds = deliveries.length > 1 
    ? L.latLngBounds(deliveries.map(d => [d.lat, d.lng]))
    : null;

  return (
    <div className={`h-full min-h-[400px] w-full rounded-3xl overflow-hidden border border-white/10 shadow-2xl ${className}`}>
      <MapContainer 
        center={defaultCenter} 
        zoom={zoom} 
        scrollWheelZoom={false}
        className="h-full w-full z-0"
      >
        {/* Dark Mode Map Layer */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        {bounds && <ChangeView bounds={bounds} />}

        {deliveries.map((delivery) => (
          <Marker 
            key={delivery.id} 
            position={[delivery.lat, delivery.lng]}
            icon={createCustomIcon(delivery.status)}
          >
            <Popup className="custom-popup">
              <div className="p-2 space-y-2 min-w-[200px]">
                <div className="flex justify-between items-start">
                  <span className="text-xs font-bold text-blue-400 font-mono">{delivery.tracking_no}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full border border-current opacity-70`}>
                    {delivery.status}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-800">{delivery.recipient_name}</p>
                  <p className="text-[10px] text-gray-500">Coordenadas: {delivery.lat.toFixed(4)}, {delivery.lng.toFixed(4)}</p>
                </div>
                <button 
                  onClick={() => window.location.href = `/dashboard/deliveries/${delivery.id}`}
                  className="w-full mt-2 py-1.5 bg-blue-600 text-white text-[10px] font-bold rounded-lg hover:bg-blue-500 transition-colors"
                >
                  Ver Detalles
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <style jsx global>{`
        .leaflet-container { background: #0f172a !important; }
        .custom-popup .leaflet-popup-content-wrapper {
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(10px);
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          padding: 0;
        }
        .custom-popup .leaflet-popup-tip { background: rgba(255, 255, 255, 0.9); }
        .leaflet-div-icon { background: transparent !important; border: none !important; }
      `}</style>
    </div>
  );
}
