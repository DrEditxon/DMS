"use client";

import React, { createContext, useContext, useEffect } from 'react';
import toast, { Toaster } from 'react-hot-toast';

export const NotificationContext = createContext({});

export default function NotificationProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'NEW_DELIVERY') {
        toast.success(data.message, {
          duration: 5000,
          position: 'top-right',
          style: {
            background: '#0f172a',
            color: '#fff',
            borderRadius: '12px',
          },
          icon: 'ðŸšš',
        });
      }
    };

    ws.onopen = () => console.log('WebSocket Connected');
    ws.onclose = () => console.log('WebSocket Disconnected');

    return () => ws.close();
  }, []);

  return (
    <NotificationContext.Provider value={{}}>
      <Toaster />
      {children}
    </NotificationContext.Provider>
  );
}

