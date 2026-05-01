"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Bell, Check, Trash2, Info } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await api.get('/notifications');
      return res.data;
    }
  });

  const markAsRead = useMutation({
    mutationFn: (id: str) => api.patch(`/notifications/${id}/read`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] })
  });

  const unreadCount = notifications?.filter((n: any) => !n.is_read).length || 0;

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-all"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 w-5 h-5 bg-red-500 text-white text-[10px] font-bold flex items-center justify-center rounded-full border-2 border-white">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-3xl shadow-2xl border border-slate-100 z-20 overflow-hidden">
            <div className="p-4 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
              <h3 className="font-bold text-slate-800">Notificaciones</h3>
              <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full uppercase">
                {unreadCount} Nuevas
              </span>
            </div>

            <div className="max-h-96 overflow-y-auto divide-y divide-slate-50">
              {notifications?.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">
                  No tienes notificaciones
                </div>
              ) : (
                notifications?.map((n: any) => (
                  <div 
                    key={n.id} 
                    className={cn(
                      "p-4 transition-colors hover:bg-slate-50 flex gap-3",
                      !n.is_read && "bg-blue-50/30"
                    )}
                  >
                    <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center shrink-0">
                      <Info className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start gap-2">
                        <p className={cn("text-sm font-bold", n.is_read ? "text-slate-600" : "text-slate-900")}>
                          {n.title}
                        </p>
                        {!n.is_read && (
                          <button 
                            onClick={() => markAsRead.mutate(n.id)}
                            className="p-1 hover:bg-emerald-100 text-emerald-600 rounded-md transition-all"
                            title="Marcar como leída"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{n.message}</p>
                      <p className="text-[10px] text-slate-400 mt-2">
                        {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="p-3 border-t border-slate-50 text-center">
              <button className="text-xs font-bold text-slate-400 hover:text-blue-600 transition-colors">
                Ver todo el historial
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
